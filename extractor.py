import os
import re
import requests
from typing import Dict, Any, Optional
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp
from dotenv import load_dotenv

load_dotenv()

# 1. Define Unified Data Schema
class VideoMetadata(BaseModel):
    video_id: str
    platform: str
    title: str
    creator: str
    follower_count: int
    views: int
    likes: int
    comments: int
    duration: int
    upload_date: str
    hashtags: list[str]
    transcript: str
    engagement_rate: float

# 2. YouTube Extraction Engine 
class YouTubeExtractor:
    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        pattern = r'(?:v=|\/shorts\/|\/embed\/|\/v\/|youtu\.be\/|\/v=)([^"&?\/ ]{11})'
        match = re.search(pattern, url)
        return match.group(1) if match else None

    def get_metadata_and_transcript(self, url: str) -> Dict[str, Any]:
        video_id = self.extract_video_id(url)
        if not video_id:
            raise ValueError("Invalid YouTube URL provided.")

        ydl_opts = {'skip_download': True, 'quiet': True, 'no_warnings': True}

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
        views = info.get('view_count') or 0
        likes = info.get('like_count') or 0
        comments = info.get('comment_count') or 0
        engagement_rate = ((likes + comments) / views * 100) if views > 0 else 0.0

        # Fetch Transcript with Aggressive Search
        try:
            # 1. List all available transcripts for the video
            transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # 2. Try to find any variation of English (manual or auto-generated)
            try:
                transcript_data = transcripts.find_transcript(['en', 'en-US', 'en-GB', 'en-IN', 'en-CA']).fetch()
            except Exception:
                # 3. If no English is found, just grab the very first available transcript (any language)
                transcript_data = next(iter(transcripts)).fetch()
                
            # Clean up the text by stripping newlines and joining
            raw_text = [t['text'].replace('\n', ' ') for t in transcript_data]
            full_transcript = " ".join(raw_text)
            
        except Exception as e:
            print(f"⚠️ YT Transcript fully unavailable (Captions disabled). Using description.")
            full_transcript = info.get('description') or "No transcript available."


        description = info.get('description') or ""
        tags = info.get('tags') or []
        if not tags: 
            tags = re.findall(r"#(\w+)", description)
            
        return {
            "video_id": video_id,
            "platform": "youtube",
            "title": info.get('title') or 'Unknown Title',
            "creator": info.get('uploader') or 'Unknown Creator',
            "follower_count": info.get('channel_follower_count') or 0,
            "views": views,
            "likes": likes,
            "comments": comments,
            "duration": info.get('duration') or 0,
            "upload_date": info.get('upload_date') or 'Unknown Date',
            "hashtags": tags, 
            "transcript": full_transcript,
            "engagement_rate": round(engagement_rate, 2)
        }


class InstagramExtractor:
    def __init__(self):
        self.api_key = os.getenv("RAPIDAPI_KEY")
        if not self.api_key:
            raise EnvironmentError("RAPIDAPI_KEY is missing from .env file.")
        
        self.api_url = "https://instagram-looter2.p.rapidapi.com/post"
        self.api_host = "instagram-looter2.p.rapidapi.com"

    def get_metadata_and_transcript(self, url: str) -> Dict[str, Any]:
        headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": self.api_host,
            "Content-Type": "application/json"
        }
        

        querystring = {"url": url} 
        
        response = requests.get(self.api_url, headers=headers, params=querystring)
        
        if response.status_code != 200:
            raise ConnectionError(f"Instagram API Failed: {response.status_code} - {response.text}")
            
        data = response.json()

        
        try:
            item = data if 'edge_media_preview_like' in data else data.get('data', {})

            views = item.get('video_view_count') or 0
            
            likes = item.get('edge_media_preview_like', {}).get('count') or item.get('like_count') or 0
            

            comments = item.get('edge_media_to_comment', {}).get('count') or item.get('comment_count') or 0
            
            engagement_rate = ((likes + comments) / views * 100) if views > 0 else 0.0
            
            
            edges = item.get('edge_media_to_caption', {}).get('edges', [])
            caption = edges[0].get('node', {}).get('text') if edges else ""
            
            hashtags = re.findall(r"#(\w+)", caption)

            comments = (
                item.get('edge_media_to_comment', {}).get('count') or 
                item.get('edge_media_preview_comment', {}).get('count') or 
                item.get('comment_count') or 0
            )

            return {
                "video_id": item.get('shortcode', 'unknown_id'),
                "platform": "instagram",
                "title": caption[:50] + "...", 
                "creator": item.get('owner', {}).get('username', 'Unknown Creator'),
                "follower_count": item.get('owner', {}).get('edge_followed_by', {}).get('count') or 0,
                "views": views,
                "likes": likes,
                "comments": comments,
                "duration": int(item.get('video_duration', 0)),
                "upload_date": str(item.get('taken_at_timestamp', 'Unknown Date')),
                "hashtags": hashtags, 
                "transcript": caption if caption else "No caption available.", 
                "engagement_rate": round(engagement_rate, 2)
            }
        except Exception as e:
            raise KeyError(f"Failed to parse Instagram API response: {e}. Check the raw JSON structure.")
        

# 4. Orchestration Entry Point & Dynamic Routing ---
def detect_platform(url: str) -> str:
    """Intelligently routes the URL to the correct microservice based on domain."""
    url_lower = url.lower()
    if "youtube.com" in url_lower or "youtu.be" in url_lower:
        return "youtube"
    elif "instagram.com" in url_lower:
        return "instagram"
    else:
        raise ValueError(f"Unsupported platform. Please provide a YouTube or Instagram URL. Invalid URL: {url}")

def extract_all_video_data(url_a: str, url_b: str) -> Dict[str, VideoMetadata]:
    yt_engine = YouTubeExtractor()
    ig_engine = InstagramExtractor()
    
    # Process Video A
    print(f"🚀 Detecting Platform for Video A...")
    platform_a = detect_platform(url_a)
    if platform_a == "youtube":
        data_a = VideoMetadata(**yt_engine.get_metadata_and_transcript(url_a))
    else:
        data_a = VideoMetadata(**ig_engine.get_metadata_and_transcript(url_a))
        
    # Process Video B
    print(f"🚀 Detecting Platform for Video B...")
    platform_b = detect_platform(url_b)
    if platform_b == "youtube":
        data_b = VideoMetadata(**yt_engine.get_metadata_and_transcript(url_b))
    else:
        data_b = VideoMetadata(**ig_engine.get_metadata_and_transcript(url_b))
    
    return {
        "video_A": data_a,
        "video_B": data_b
    }

if __name__ == "__main__":
    # For Testing Purpose
    sample_yt_1 = "https://www.youtube.com/shorts/dQw4w9WgXcQ" 
    sample_yt_2 = "https://www.youtube.com/shorts/3JZ_D3ELwOQ"
    
    results = extract_all_video_data(sample_yt_1, sample_yt_2)
    
    print("\n✅ Dynamic Extraction Complete!")
    print(f"Video A ({results['video_A'].platform}) | Creator: {results['video_A'].creator}")
    print(f"Video B ({results['video_B'].platform}) | Creator: {results['video_B'].creator}")