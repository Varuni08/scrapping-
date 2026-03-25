import os
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
CSE_ID = os.getenv("GOOGLE_CSE_ID")

def search_google_web(query, num_results=10):
    """
    Uses Google Custom Search API to find websites.
    """
    if not API_KEY or not CSE_ID:
        return ["Error: GOOGLE_API_KEY or GOOGLE_CSE_ID missing in .env"]

    try:
        service = build("customsearch", "v1", developerKey=API_KEY)
        # cx = custom search engine ID
        result = service.cse().list(q=query, cx=CSE_ID, num=num_results).execute()
        
        items = result.get("items", [])
        
        formatted_results = []
        for item in items:
            title = item.get("title")
            link = item.get("link")
            snippet = item.get("snippet", "No description available.")
            formatted_results.append(f"Title: {title}\nURL: {link}\nSnippet: {snippet}")
            
        return formatted_results

    except Exception as e:
        return [f"Google Search Error: {str(e)}"]

def search_youtube_videos(query, max_results=10):
    """
    Uses YouTube Data API v3 to find videos.
    """
    if not API_KEY:
        return ["Error: GOOGLE_API_KEY missing in .env"]

    try:
        youtube = build("youtube", "v3", developerKey=API_KEY)
        
        request = youtube.search().list(
            part="snippet",
            maxResults=max_results,
            q=query,
            type="video" # Ensure we only get videos, not channels/playlists
        )
        response = request.execute()
        
        formatted_results = []
        for item in response.get("items", []):
            video_id = item["id"]["videoId"]
            title = item["snippet"]["title"]
            desc = item["snippet"]["description"]
            channel = item["snippet"]["channelTitle"]
            link = f"https://www.youtube.com/watch?v={video_id}"
            
            formatted_results.append(f"Title: {title}\nChannel: {channel}\nURL: {link}\nDescription: {desc}")
            
        return formatted_results

    except Exception as e:
        return [f"YouTube API Error: {str(e)}"]