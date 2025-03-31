# src/tools.py
from typing import List, Dict, Any, Optional
import re

def search_youtube_videos(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """
    Search for YouTube videos based on the query.
    """
    try:
        import requests
        import json
        import re
        
        # Format query for URL
        formatted_query = query.replace(' ', '+')
        
        # Make a direct request to YouTube
        url = f"https://www.youtube.com/results?search_query={formatted_query}"
        
        # Create a session without proxies
        session = requests.Session()
        session.proxies = {}
        
        response = session.get(url)
        
        if response.status_code != 200:
            return [{"error": f"Failed to fetch search results: HTTP {response.status_code}"}]
        
        # Extract initial data
        content = response.text
        initial_data_match = re.search(r'var ytInitialData = (.+?);</script>', content)
        
        if not initial_data_match:
            return [{"error": "Could not extract video data from YouTube response"}]
        
        # Parse the JSON data
        initial_data = json.loads(initial_data_match.group(1))
        
        # Extract video information
        videos = []
        try:
            contents = initial_data['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents']
            
            for section in contents:
                if 'itemSectionRenderer' not in section:
                    continue
                    
                items = section['itemSectionRenderer']['contents']
                
                for item in items:
                    if 'videoRenderer' not in item:
                        continue
                        
                    video_data = item['videoRenderer']
                    
                    # Extract video title
                    title = video_data['title']['runs'][0]['text']
                    
                    # Extract video URL
                    video_id = video_data['videoId']
                    url = f"https://www.youtube.com/watch?v={video_id}"
                    
                    # Extract channel name
                    channel = video_data['ownerText']['runs'][0]['text']
                    
                    videos.append({
                        "title": title,
                        "url": url,
                        "channel": channel
                    })
                    
                    # Limit results
                    if len(videos) >= max_results:
                        break
                
                if len(videos) >= max_results:
                    break
        except (KeyError, IndexError) as e:
            # If there's an error parsing, return the error
            return [{"error": f"Error parsing YouTube results: {str(e)}"}]
        
        return videos if videos else [{"error": "No videos found"}]
        
    except Exception as e:
        return [{"error": f"Error searching YouTube: {str(e)}"}]

def extract_video_transcript(video_url: str) -> str:
    """
    Extract the transcript from a YouTube video.
    """
    try:
        # Extract video ID from URL
        video_id = None
        if "youtube.com/watch" in video_url:
            match = re.search(r"v=([^&]+)", video_url)
            if match:
                video_id = match.group(1)
        elif "youtu.be/" in video_url:
            video_id = video_url.split("youtu.be/")[1].split("?")[0]
        
        if not video_id:
            return "Invalid YouTube URL format"
            
        # Load transcript
        from youtube_transcript_api import YouTubeTranscriptApi
        
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = " ".join([item['text'] for item in transcript_list])
        
        return transcript_text
    except Exception as e:
        return f"Error extracting transcript: {str(e)}"

def analyze_channel_content(channel_name: str, video_count: int = 3) -> str:
    """
    Analyze the content of a YouTube channel by examining its videos.
    """
    try:
        import requests
        import json
        import re
        
        # Format channel name for search
        formatted_query = channel_name.replace(' ', '+')
        
        # Make a direct request to YouTube
        url = f"https://www.youtube.com/results?search_query={formatted_query}&sp=EgIQAg%3D%3D"  # Channel filter
        
        # Create a session without proxies
        session = requests.Session()
        session.proxies = {}
        
        response = session.get(url)
        
        if response.status_code != 200:
            return f"Failed to fetch channel: HTTP {response.status_code}"
        
        # Extract initial data
        content = response.text
        initial_data_match = re.search(r'var ytInitialData = (.+?);</script>', content)
        
        if not initial_data_match:
            return "Could not extract channel data from YouTube response"
        
        # Parse the JSON data
        initial_data = json.loads(initial_data_match.group(1))
        
        # Find the channel
        channel_title = None
        channel_id = None
        
        try:
            contents = initial_data['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents']
            
            for section in contents:
                if 'itemSectionRenderer' not in section:
                    continue
                    
                items = section['itemSectionRenderer']['contents']
                
                for item in items:
                    if 'channelRenderer' in item:
                        channel_data = item['channelRenderer']
                        channel_title = channel_data['title']['simpleText']
                        channel_id = channel_data['channelId']
                        break
                
                if channel_id:
                    break
                    
            if not channel_id:
                return f"Channel '{channel_name}' not found"
                
            # Now get videos from this channel
            channel_url = f"https://www.youtube.com/channel/{channel_id}/videos"
            channel_response = session.get(channel_url)
            
            if channel_response.status_code != 200:
                return f"Failed to fetch channel videos: HTTP {channel_response.status_code}"
                
            # Extract video data
            channel_content = channel_response.text
            channel_data_match = re.search(r'var ytInitialData = (.+?);</script>', channel_content)
            
            if not channel_data_match:
                return "Could not extract video data from channel page"
                
            channel_data = json.loads(channel_data_match.group(1))
            
            # Extract videos
            video_info = []
            
            try:
                tabs = channel_data['contents']['twoColumnBrowseResultsRenderer']['tabs']
                videos_tab = next((tab for tab in tabs if tab.get('tabRenderer', {}).get('title') == 'Videos'), None)
                
                if not videos_tab:
                    return f"No videos tab found for channel '{channel_title}'"
                    
                videos_content = videos_tab['tabRenderer']['content']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents'][0]['gridRenderer']['items']
                
                for i, video_item in enumerate(videos_content):
                    if i >= video_count:
                        break
                        
                    if 'gridVideoRenderer' not in video_item:
                        continue
                        
                    video_renderer = video_item['gridVideoRenderer']
                    
                    title = video_renderer['title']['runs'][0]['text']
                    duration = video_renderer.get('thumbnailOverlays', [{}])[0].get('thumbnailOverlayTimeStatusRenderer', {}).get('text', {}).get('simpleText', 'Unknown')
                    views = video_renderer.get('viewCountText', {}).get('simpleText', 'Unknown views')
                    published = video_renderer.get('publishedTimeText', {}).get('simpleText', 'Unknown')
                    
                    video_info.append({
                        "title": title,
                        "duration": duration,
                        "views": views,
                        "published": published
                    })
                    
            except (KeyError, IndexError) as e:
                return f"Error parsing channel videos: {str(e)}"
                
            # Format analysis
            analysis = f"Analysis of '{channel_title}' channel:\n\n"
            analysis += f"Top {len(video_info)} videos:\n"
            
            for i, video in enumerate(video_info):
                analysis += f"{i+1}. {video['title']}\n"
                analysis += f"   Duration: {video['duration']}, Views: {video['views']}, Published: {video['published']}\n"
                
            return analysis
                
        except (KeyError, IndexError) as e:
            return f"Error analyzing channel: {str(e)}"
            
    except Exception as e:
        return f"Error analyzing channel: {str(e)}"