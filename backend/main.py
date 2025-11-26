import os
import logging
import shutil
import traceback
from dotenv import load_dotenv

load_dotenv()

# CRITICAL: Monkey patch httpx.AsyncClient BEFORE importing any bilibili_api code
# bilibili-api-python uses 'proxy' parameter but httpx 0.23.3 expects 'proxies'
import httpx
_original_async_client_init = httpx.AsyncClient.__init__

def _patched_async_client_init(self, *args, proxy=None, proxies=None, **kwargs):
    """修复bilibili_api传入proxy参数的问题，httpx 0.23.3需要proxies参数"""
    if proxy is not None and proxies is None:
        proxies = proxy
    _original_async_client_init(self, *args, proxies=proxies, **kwargs)

httpx.AsyncClient.__init__ = _patched_async_client_init


from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List

from services.youtube_service import YouTubeService
try:
    from services.bilibili_service import BilibiliService
    BILIBILI_AVAILABLE = True
except ImportError:
    print("WARNING: bilibili-api-python not installed. Bilibili analysis will be unavailable.")
    BilibiliService = None
    BILIBILI_AVAILABLE = False
from services.vision_service import VisionService
from services.analysis_service import AnalysisService
from services.report_generator import ReportGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="YouTube Channel Style Analyzer API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*\.vercel\.app|http://localhost:\d+|https://decode-any-you-tuber\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Services
youtube_service = YouTubeService()
bilibili_service = BilibiliService() if BILIBILI_AVAILABLE else None
vision_service = VisionService()
analysis_service = AnalysisService()
report_generator = ReportGenerator()

class AnalyzeChannelRequest(BaseModel):
    channel_url: str
    video_limit: int = 3 # Analyze top 3 recent videos to save time/tokens
    language: str = "zh" # "zh" or "en"
    platform: str = "youtube" # "youtube" or "bilibili"

@app.get("/")
async def root():
    return {"message": "YouTube Channel Style Analyzer API is running"}

@app.post("/analyze_channel")
async def analyze_channel(request: AnalyzeChannelRequest):
    try:
        try:
            # 1. Fetch Recent Videos List
            logger.info(f"Fetching recent videos for channel: {request.channel_url}")
            recent_videos = youtube_service.get_channel_recent_videos(request.channel_url, limit=request.video_limit)
            
            if not recent_videos:
                raise HTTPException(status_code=404, detail="No videos found or invalid channel URL")

            # 2. Fetch Details for Each Video (Parallel)
            import asyncio

            async def fetch_video_details(video):
                logger.info(f"Fetching details for video: {video['title']}")
                try:
                    # Run blocking calls in a separate thread
                    details = await asyncio.to_thread(youtube_service.get_video_details, video['url'])
                    
                    # Get Transcript
                    transcript = await asyncio.to_thread(youtube_service.get_transcript, details['id'])
                    details['transcript'] = transcript
                    
                    # Download Thumbnail
                    thumb_path = None
                    if details.get('thumbnail'):
                        thumb_path = await asyncio.to_thread(vision_service.download_image, details['thumbnail'])
                    
                    return details, thumb_path
                except Exception as e:
                    logger.error(f"Error fetching details for {video['title']}: {e}")
                    return None, None

            # Execute all fetch tasks concurrently
            tasks = [fetch_video_details(video) for video in recent_videos]
            results = await asyncio.gather(*tasks)
            
            detailed_videos = []
            thumbnails = []
            
            for details, thumb_path in results:
                if details:
                    detailed_videos.append(details)
                if thumb_path:
                    thumbnails.append(thumb_path)

            # 3. AI Analysis (Channel Level)
            logger.info("Starting AI Channel Analysis...")
            analysis_result = analysis_service.analyze_channel(
                recent_videos=recent_videos,
                detailed_videos=detailed_videos,
                thumbnails=thumbnails,
                language=request.language,
                platform="youtube"  # 传递平台信息
            )

            # 4. Generate Report
            markdown_report = report_generator.generate_markdown_report(analysis_result, language=request.language)

            return {
                "status": "success",
                "data": analysis_result,
                "report": markdown_report
            }

        except Exception as e:
            logger.error(f"Channel analysis failed: {e}")
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup temp directory to ensure no persistence
        logger.info("Cleaning up temp directory...")
        shutil.rmtree("temp", ignore_errors=True)

@app.post("/analyze_bilibili_creator")
async def analyze_bilibili_creator(request: AnalyzeChannelRequest):
    """
    分析B站UP主风格
    功能与analyze_channel完全一致,只是使用bilibili_service作为数据源
    """
    # Check if Bilibili service is available
    if not BILIBILI_AVAILABLE or bilibili_service is None:
        raise HTTPException(
            status_code=503, 
            detail="Bilibili analysis is currently unavailable. The bilibili-api-python package is not installed."
        )
    
    try:
        try:
            # 1. Fetch Recent Videos List from Bilibili
            logger.info(f"Fetching recent videos for Bilibili creator: {request.channel_url}")
            recent_videos = await bilibili_service.get_user_recent_videos(request.channel_url, limit=request.video_limit)
            
            if not recent_videos:
                raise HTTPException(status_code=404, detail="No videos found or invalid Bilibili user URL")

            # 2. Fetch Details for Each Video (Parallel)
            import asyncio

            async def fetch_video_details(video):
                logger.info(f"Fetching details for video: {video['title']}")
                try:
                    # Directly await async methods
                    details = await bilibili_service.get_video_details(video['url'])
                    
                    # Get Subtitle
                    subtitle = await bilibili_service.get_subtitle(details['id'])
                    details['transcript'] = subtitle
                    
                    # Download Thumbnail
                    thumb_path = None
                    if details.get('thumbnail'):
                        thumb_path = await asyncio.to_thread(vision_service.download_image, details['thumbnail'])
                    
                    return details, thumb_path
                except Exception as e:
                    logger.error(f"Error fetching details for {video['title']}: {e}")
                    return None, None

            # Execute all fetch tasks concurrently
            tasks = [fetch_video_details(video) for video in recent_videos]
            results = await asyncio.gather(*tasks)
            
            detailed_videos = []
            thumbnails = []
            
            for details, thumb_path in results:
                if details:
                    detailed_videos.append(details)
                if thumb_path:
                    thumbnails.append(thumb_path)

            # 3. AI Analysis (Channel Level) - 完全复用
            logger.info("Starting AI Bilibili Creator Analysis...")
            analysis_result = analysis_service.analyze_channel(
                recent_videos=recent_videos,
                detailed_videos=detailed_videos,
                thumbnails=thumbnails,
                language=request.language,
                platform="bilibili"  # 传递平台信息
            )

            # 4. Generate Report - 完全复用
            markdown_report = report_generator.generate_markdown_report(analysis_result, language=request.language)

            return {
                "status": "success",
                "data": analysis_result,
                "report": markdown_report
            }

        except Exception as e:
            logger.error(f"Bilibili creator analysis failed: {e}")
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup temp directory to ensure no persistence
        logger.info("Cleaning up temp directory...")
        shutil.rmtree("temp", ignore_errors=True)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

