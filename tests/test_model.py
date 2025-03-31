# src/test_model.py
from ..src.agent import get_llm, create_youtube_agent
from ..src.tools import search_youtube_videos

def test_llm():
    """Test if the Ollama model is working properly"""
    print("Testing Ollama model: llama3.3:70b-instruct-q2_K")
    
    try:
        # Initialize the model
        llm = get_llm("llama3.3:70b-instruct-q2_K")
        
        # Test basic response
        response = llm.invoke("Write a short poem about YouTube")
        print("\nLLM Response:")
        print(response)
        print("\nModel test completed successfully!")
        return True
    except Exception as e:
        print(f"\nError testing model: {str(e)}")
        return False

def test_agent():
    """Test if the agent can use a tool"""
    print("\nTesting YouTube Agent with a simple tool call...")
    
    try:
        # Create agent with just the search tool
        agent = create_youtube_agent(
            tools=[search_youtube_videos],
            model_name="llama3.3:70b-instruct-q2_K",
            verbose=True
        )
        
        # Test agent with a simple query
        response = agent.invoke({"input": "Find videos about the latest iPhone"})
        print("\nAgent Response:")
        print(response["output"])
        print("\nAgent test completed successfully!")
        return True
    except Exception as e:
        print(f"\nError testing agent: {str(e)}")
        return False

if __name__ == "__main__":
    if test_llm():
        test_agent()