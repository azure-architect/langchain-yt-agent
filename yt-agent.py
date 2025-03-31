# yt-agent.py
from src.agent import create_youtube_agent
from langchain_core.tools import Tool
from src.tools import search_youtube_videos, extract_video_transcript, analyze_channel_content
from src.agent import ollama_model



def main():
    """Main application entry point"""
    print("Initializing YouTube Agent with Ollama...")
    
    # Create list of tools as proper Tool objects
    youtube_tools = [
        Tool(
            name="search_youtube_videos",
            func=search_youtube_videos,
            description="Search for YouTube videos based on the query."
        ),
        Tool(
            name="extract_video_transcript",
            func=extract_video_transcript,
            description="Extract the transcript from a YouTube video."
        ),
        Tool(
            name="analyze_channel_content",
            func=analyze_channel_content,
            description="Analyze the content of a YouTube channel by examining its videos."
        )
    ]
    
    # Get model name from user or use default
    model_name = input("Enter Ollama model name (default: ollama_model): ").strip() or "mistral:latest"
    
    # Ask if debug mode should be enabled
    debug_mode = input("Enable debug mode to see raw LLM responses? (y/n): ").lower().startswith('y')
    
    # Create agent
    agent = create_youtube_agent(
        tools=youtube_tools,
        model_name=model_name,
        verbose=True,
        debug=debug_mode
    )
    
    print(f"YouTube Agent ready with Ollama model: {model_name}")

    print("Type 'exit' to quit")
    
    # Simple command loop
    while True:
        user_input = input("\nWhat would you like to know about YouTube content? ")
        
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break
            
        try:
            response = agent.invoke({"input": user_input})
            print(f"\nAgent response: {response['output']}")
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
