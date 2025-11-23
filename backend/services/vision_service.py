import os
import cv2
import requests
import base64
import logging
import yt_dlp
import uuid
from PIL import Image
from io import BytesIO
from typing import List, Optional

logger = logging.getLogger(__name__)

class VisionService:
    def __init__(self, temp_dir: str = "temp"):
        self.temp_dir = temp_dir
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)

    def download_image(self, url: str) -> Optional[str]:
        """
        Downloads an image from URL and returns the local path.
        """
        try:
            response = requests.get(url)
            if response.status_code == 200:
                # Use UUID to prevent filename collisions
                filename = os.path.join(self.temp_dir, f"thumbnail_{uuid.uuid4()}.jpg")
                with open(filename, "wb") as f:
                    f.write(response.content)
                return filename
            return None
        except Exception as e:
            logger.error(f"Error downloading image {url}: {e}")
            return None

    def download_video(self, video_url: str) -> Optional[str]:
        """
        Downloads the video (lowest quality for speed) and returns the path.
        """
        # Use UUID for video filename
        video_id = str(uuid.uuid4())
        output_template = os.path.join(self.temp_dir, f'video_{video_id}.%(ext)s')
        
        ydl_opts = {
            'format': 'worstvideo[ext=mp4]+worstaudio[ext=m4a]/worst[ext=mp4]/worst',
            'outtmpl': output_template,
            'quiet': True,
            'overwrites': True,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
                # yt-dlp might save as .mp4 or other ext, but we requested mp4 preference
                # We need to find the actual file created
                expected_path = os.path.join(self.temp_dir, f"video_{video_id}.mp4")
                if os.path.exists(expected_path):
                    return expected_path
                
                # Fallback: check for any file with that prefix
                for f in os.listdir(self.temp_dir):
                    if f.startswith(f"video_{video_id}"):
                        return os.path.join(self.temp_dir, f)
                        
                return None
        except Exception as e:
            logger.error(f"Error downloading video {video_url}: {e}")
            return None

    def extract_keyframes(self, video_path: str, interval_seconds: int = 10, max_frames: int = 10) -> List[str]:
        """
        Extracts keyframes from the video at specified intervals.
        Returns a list of local paths to the extracted frames.
        """
        frames = []
        if not video_path or not os.path.exists(video_path):
            return frames

        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps == 0:
            return frames
            
        frame_interval = int(fps * interval_seconds)
        count = 0
        extracted_count = 0

        while cap.isOpened() and extracted_count < max_frames:
            ret, frame = cap.read()
            if not ret:
                break

            if count % frame_interval == 0:
                # Use UUID for frame filename to avoid collisions if multiple videos are processed
                frame_path = os.path.join(self.temp_dir, f"frame_{uuid.uuid4()}.jpg")
                cv2.imwrite(frame_path, frame)
                frames.append(frame_path)
                extracted_count += 1
            
            count += 1

        cap.release()
        return frames

    def encode_image(self, image_path: str) -> str:
        """
        Encodes an image file to base64 string.
        """
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"Error encoding image {image_path}: {e}")
            return ""
