# src/agent.py

from typing import List, Dict, Any
import re
import json
from langchain_core.tools import Tool
ollama_model='llama3-groq-tool-use:latest'

def get_llm(model_name="ollama_model", debug=False):
    """Initialize and return an LLM using Ollama with optional debug mode"""
    from langchain_ollama import OllamaLLM
    
    if debug:
        # Create a wrapper class that prints raw responses
        class DebugOllamaLLM(OllamaLLM):
            def invoke(self, prompt, **kwargs):
                if isinstance(prompt, str):
                    print("\n--- DEBUG: PROMPT TO LLM ---")
                    print(prompt)
                else:
                    print("\n--- DEBUG: STRUCTURED PROMPT TO LLM ---")
                    print(str(prompt))
                
                response = super().invoke(prompt, **kwargs)
                
                print("\n--- DEBUG: RAW LLM RESPONSE ---")
                print(response)
                print("-------------------------------\n")
                return response
                
        return DebugOllamaLLM(
            model=model_name,
            temperature=0.1
        )
    else:
        return OllamaLLM(
            model=model_name,
            temperature=0.1
        )

def create_youtube_agent(tools: List[Tool], model_name="ollama_model", verbose=True, debug=False):
    """Create a very simple YouTube agent that doesn't rely on complex LangChain components"""
    
    # Initialize LLM
    llm = get_llm(model_name, debug=debug)
    
    # Build a manual prompt template
    tool_descriptions = "\n".join([f"- {tool.name}: {tool.description}" for tool in tools])
        
    prompt_template = """You are a YouTube content analysis assistant that helps users discover and understand YouTube videos and channels.

    For a truly comprehensive analysis, you should typically use multiple tools in sequence to gather complete information:
    1. First search for relevant videos
    2. Then extract transcripts from the most promising results (using the exact URL returned by search)
    3. Finally analyze the channel to understand the creator's credibility and content focus

    Available tools:
    {tool_descriptions}

    To use a tool, you must respond in this exact format:

    <json>
    {{
    "action": "tool_name",
    "action_input": "input to the tool"
    }}
    </json>

    For example, to search for videos about Python programming:
    <json>
    {{
    "action": "search_youtube_videos",
    "action_input": "python programming"
    }}
    </json>

    And after getting search results, to extract a transcript:
    <json>
    {{
    "action": "extract_video_transcript",
    "action_input": "https://www.youtube.com/watch?v=actual_video_id"
    }}
    </json>

    After using a tool, examine the results carefully to determine if you need additional information from other tools.
    Always use the exact URLs returned by the search tool when extracting transcripts or analyzing channels.

    When you have a final answer that doesn't require using more tools, provide your response in plain text without using the json format.
    Your final answer should synthesize information from all tools used and provide valuable insights the user couldn't easily find on their own.

    Think step by step to solve the user's request thoroughly. Always aim to provide comprehensive analysis rather than basic information.

    User query: {user_query}
    """
    
    # Create a simple executor function
    def simple_agent_executor(query):
        # Format the prompt with the user query - FIX HERE
        # Replace the placeholder with the actual query
        formatted_prompt = prompt_template.format(
            tool_descriptions=tool_descriptions,
            user_query=query
        )
        
        # Keep track of the conversation context
        conversation_context = formatted_prompt
        
        # Maximum number of tool-calling iterations
        max_iterations = 5
        iterations = 0
        
        while iterations < max_iterations:
            if verbose:
                print(f"\nIteration {iterations + 1}:")
            
            # Get LLM response
            response = llm.invoke(conversation_context)
            
            # Try to extract JSON from the response
            json_pattern = r'<json>\s*({.*?})\s*</json>|({.*?})'
            json_matches = re.findall(json_pattern, response, re.DOTALL)
            
            # Flatten and filter matches
            json_candidates = [m[0] if m[0] else m[1] for m in json_matches if m[0] or m[1]]
            
            tool_name = None
            tool_input = None
            
            # Try to parse each JSON candidate
            for json_str in json_candidates:
                try:
                    parsed = json.loads(json_str)
                    tool_name = parsed.get('action') or parsed.get('tool')
                    tool_input = parsed.get('action_input') or parsed.get('tool_input') or parsed.get('input')
                    
                    if tool_name and tool_name in [t.name for t in tools]:
                        break
                except Exception as e:
                    if verbose:
                        print(f"Failed to parse JSON: {str(e)}")
                    continue
            
            # If we found a valid tool call
            if tool_name and tool_input:
                if verbose:
                    print(f"Using tool: {tool_name}")
                    print(f"Tool input: {tool_input}")
                
                # Find the tool
                tool = next((t for t in tools if t.name == tool_name), None)
                
                if tool:
                    try:
                        # Execute the tool
                        tool_result = tool.invoke(tool_input)
                        
                        if verbose:
                            print(f"Tool result: {str(tool_result)[:100]}...")
                        
                        # Add the tool result to the conversation
                        tool_execution_text = f"\nTool: {tool_name}\nTool Input: {tool_input}\nTool Result: {tool_result}\n\nBased on this information, provide a final answer or use another tool if needed."
                        conversation_context = conversation_context + "\n" + response + tool_execution_text
                    except Exception as e:
                        if verbose:
                            print(f"Error executing tool: {str(e)}")
                        tool_execution_text = f"\nError executing tool {tool_name}: {str(e)}\nPlease try a different approach or provide an answer based on what you know."
                        conversation_context = conversation_context + "\n" + response + tool_execution_text
                else:
                    if verbose:
                        print(f"Unknown tool: {tool_name}")
                    tool_execution_text = f"\nTool '{tool_name}' is not available. Please use one of the available tools."
                    conversation_context = conversation_context + "\n" + response + tool_execution_text
            else:
                # If no tool call was detected, treat the response as a final answer
                # Clean up any markdown or JSON artifacts
                clean_response = re.sub(r'<json>.*?</json>', '', response, flags=re.DOTALL)
                clean_response = re.sub(r'{.*?}', '', clean_response, flags=re.DOTALL)
                clean_response = clean_response.replace('Final Answer:', '').strip()
                
                if verbose:
                    print("Final answer provided.")
                
                return clean_response
            
            iterations += 1
        
        # If we've reached the maximum number of iterations, generate a final response
        final_prompt = conversation_context + "\n\nPlease provide a final answer based on all the information above."
        final_response = llm.invoke(final_prompt)
        
        # Clean up the final response
        clean_response = re.sub(r'<json>.*?</json>', '', final_response, flags=re.DOTALL)
        clean_response = re.sub(r'{.*?}', '', clean_response, flags=re.DOTALL)
        clean_response = clean_response.replace('Final Answer:', '').strip()
        
        return clean_response
    
    # Create an interface that matches LangChain's AgentExecutor
    class SimpleAgentExecutor:
        def __init__(self, executor_function):
            self.executor_function = executor_function
        
        def invoke(self, inputs):
            result = self.executor_function(inputs.get("input", ""))
            return {"output": result}
            
    return SimpleAgentExecutor(simple_agent_executor)