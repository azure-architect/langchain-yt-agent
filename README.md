# YouTube Content Analysis Agent

## Overview
The YouTube Content Analysis Agent is a sophisticated tool that helps users discover, analyze, and extract structured content from YouTube videos. Built using LangChain and Ollama, this agent leverages local LLM models to provide comprehensive analysis of YouTube content for research, learning, or content creation purposes.

## Features
- **Video Search**: Find relevant YouTube videos based on specific queries
- **Transcript Extraction**: Pull and analyze the transcript content from videos
- **Channel Analysis**: Evaluate the credibility and content focus of YouTube channels
- **Multi-Tool Sequential Analysis**: Process video content through multiple analytical steps
- **Structured Output**: Organize findings into publication-ready formats
- **Local LLM Integration**: Runs entirely on your local machine using Ollama models

## Technical Architecture

### Main Components
1. **Entry Point (`yt-agent.py`)**: Controls user interaction and initializes the agent
2. **Agent Implementation (`src/agent.py`)**: Custom agent logic for handling LLM interactions and tool execution
3. **YouTube Tools (`src/tools.py`)**: Set of tools for interacting with YouTube content

### Tools
- `search_youtube_videos`: Searches YouTube for videos matching a query
- `extract_video_transcript`: Extracts and processes transcripts from YouTube videos
- `analyze_channel_content`: Analyzes a YouTube channel's content and credibility

### Custom Agent Implementation
We've implemented a simplified agent that avoids compatibility issues with local LLMs by:
- Using a custom prompt template to guide the model
- Implementing robust JSON parsing with regex pattern matching
- Handling multiple JSON output formats from different models
- Including comprehensive error recovery mechanisms
- Enabling a debug mode to see raw LLM responses

### Execution Flow
1. User inputs a query about YouTube content
2. Agent formulates a plan using available tools
3. Agent executes search tool to find relevant videos
4. Agent analyzes search results to determine next steps
5. Agent can extract transcripts from promising videos
6. Agent can analyze channel content for deeper insights
7. Agent synthesizes all gathered information into a structured response

## Installation & Setup

### Prerequisites
- Python 3.8+
- pip
- Ollama installed locally (https://ollama.ai/download)

### Installation Steps
1. Clone the repository:
   ```
   git clone https://github.com/yourusername/yt-agent.git
   cd yt-agent
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv yt-agent_env
   source yt-agent_env/bin/activate  # On Windows: yt-agent_env\Scripts\activate
   ```

3. Install required packages:
   ```
   pip install -r requirements.txt
   ```

4. Ensure Ollama is running and has at least one model installed (recommended: gemma3:27b or mistral:latest)

## Usage

### Basic Usage
Run the agent using:
```
python yt-agent.py
```

Follow the prompts to:
1. Select an Ollama model (defaults to gemma3:27b)
2. Choose whether to enable debug mode
3. Enter your YouTube content query

### Example Queries
- "ollama python library"
- "langchain ollama client"
- "polyester body filler"

### Output Format
The agent provides comprehensive responses that include:
- Relevant videos with titles, URLs, and channel names
- Content summaries based on available information
- Structured analysis of concepts, steps, or techniques (when available)

## Advanced Features

### Debug Mode
Enable debug mode to see:
- Raw prompts sent to the LLM
- Unprocessed LLM responses
- Tool execution details

### Prompt Customization
The agent uses a specialized prompt template that can be customized in `src/agent.py`:
```python
prompt_template = """You are a YouTube content analysis assistant that helps users discover and understand YouTube videos and channels.

For a truly comprehensive analysis, you should typically use multiple tools in sequence to gather complete information:
1. First search for relevant videos
2. Then extract transcripts from the most promising results
3. Finally analyze the channel to understand the creator's credibility and content focus

Available tools:
{tool_descriptions}

...
```

### Structured Output for Publishing
The agent can be configured to produce publishing-ready structured content with sections for:
- Title and summary
- Key concepts and prerequisites
- Installation and usage steps
- Code examples
- Common issues and solutions
- Expert insights and resources

## Current Limitations
- Transcript extraction requires exact video URL formatting
- Channel analysis depth depends on available channel data
- Content synthesis quality varies by LLM model capability
- Handling of very long videos or transcripts may be limited
- YouTube's page structure changes can affect scraping reliability

## Future Improvements
- Enhanced transcript parsing for technical content
- Better error recovery for failed tool executions
- Specialized content extraction for programming tutorials
- Improved channel credibility assessment
- Support for more output formats (Markdown, HTML, etc.)
- Caching mechanism for frequently accessed content

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
- LangChain for providing the framework for connecting LLMs with tools
- Ollama for enabling local LLM execution
- YouTube for being a valuable source of educational content
