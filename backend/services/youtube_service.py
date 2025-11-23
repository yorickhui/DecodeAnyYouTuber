import os
import json
import logging
from typing import Optional, Dict, List, Any
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from utils.helpers import extract_video_id

logger = logging.getLogger(__name__)

class YouTubeService:
    def __init__(self):
        # No API key needed for yt-dlp based extraction
        pass

    def get_channel_recent_videos(self, channel_url: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Fetches the most recent N videos from a channel using yt-dlp.
        Returns a list of video metadata dictionaries.
        """
        # Use /videos tab to ensure we get uploaded videos, not the channel home
        if not channel_url.endswith('/videos'):
            channel_url = f"{channel_url.rstrip('/')}/videos"

        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True, # Fast extraction, only metadata
            'playlistend': limit, # Limit number of videos
            # 'ignoreerrors': True, # Removed to allow errors to propagate
        }
        
        videos = []
        try:
            # Allow exceptions to propagate to the caller (main.py), but handle the closed file issue
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # This extracts the channel/playlist info
                result = ydl.extract_info(channel_url, download=False)
                
                if result and 'entries' in result:
                    for entry in result['entries']:
                        if not entry:
                            continue
                            
                        video_id = entry.get("id")
                        # Basic validation: Video IDs are usually 11 chars. Channel IDs are longer (24 chars).
                        if not video_id or len(video_id) > 15: 
                            continue

                        videos.append({
                            "id": video_id,
                            "title": entry.get("title"),
                            "url": entry.get("url") or f"https://www.youtube.com/watch?v={video_id}",
                            "duration": entry.get("duration"),
                            "view_count": entry.get("view_count"),
                            "upload_date": entry.get("upload_date"),
                        })
        except Exception as e:
            # Handle the specific closed file error that happens on 404s in some envs
            # Also handle standard 404s from yt-dlp
            error_msg = str(e).lower()
            if "closed file" in error_msg or "not found" in error_msg or "404" in error_msg:
                 raise ValueError(f"Could not fetch channel. Please check if the URL is correct and the channel exists.") from e
            raise e
        
        return videos

    def get_video_details(self, video_url: str, fetch_comments: bool = True) -> Dict[str, Any]:
        """
        Fetches detailed metadata for a single video, optionally including comments.
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'getcomments': fetch_comments, # Try to fetch comments
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                
                # Extract comments if available
                comments = []
                if fetch_comments and 'comments' in info:
                    # yt-dlp returns a list of comment dicts
                    # We take top 20 for analysis
                    if info['comments']:
                        for c in info['comments'][:20]:
                            if isinstance(c, dict) and 'text' in c:
                                comments.append(c['text'])
                
                return {
                    "id": info.get("id"),
                    "title": info.get("title"),
                    "description": info.get("description"),
                    "view_count": info.get("view_count"),
                    "like_count": info.get("like_count"),
                    "duration": info.get("duration"),
                    "upload_date": info.get("upload_date"),
                    "uploader": info.get("uploader"),
                    "channel_id": info.get("channel_id"),
                    "tags": info.get("tags", []),
                    "thumbnail": info.get("thumbnail"),
                    "categories": info.get("categories", []),
                    "comments": comments
                }
        except Exception as e:
            logger.error(f"Error fetching metadata for {video_url}: {e}")
            # Return minimal info if full fetch fails
            return {"id": extract_video_id(video_url), "error": str(e)}

    def get_transcript(self, video_id: str) -> str:
        """
        Fetches video transcript using youtube-transcript-api.
        """
        if not video_id:
            return ""
            
        try:
            # Check if list_transcripts exists
            if hasattr(YouTubeTranscriptApi, 'list_transcripts'):
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                try:
                    transcript = transcript_list.find_transcript(['zh-CN', 'zh-TW', 'zh-HK', 'en'])
                except:
                    try:
                        transcript = transcript_list.find_generated_transcript(['zh-CN', 'zh-TW', 'zh-HK', 'en'])
                    except:
                        transcript = next(iter(transcript_list))
                transcript_data = transcript.fetch()
            elif hasattr(YouTubeTranscriptApi, 'get_transcript'):
                # Fallback for older versions
                transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=['zh-CN', 'zh-TW', 'zh-HK', 'en'])
            else:
                logger.error("YouTubeTranscriptApi missing both list_transcripts and get_transcript.")
                return ""

            full_text = " ".join([item['text'] for item in transcript_data])
            return full_text
            
        except (TranscriptsDisabled, NoTranscriptFound):
            logger.warning(f"No transcript found for video {video_id}")
            return ""
        except Exception as e:
            logger.error(f"Error fetching transcript for {video_id}: {e}")
            return ""
