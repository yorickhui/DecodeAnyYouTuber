import re
from urllib.parse import urlparse, parse_qs

def extract_video_id(url: str) -> str:
    """
    Extracts the video ID from a YouTube URL.
    Supports various formats:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    - https://www.youtube.com/v/VIDEO_ID
    """
    parsed_url = urlparse(url)
    
    if parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    
    if parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
        if parsed_url.path == '/watch':
            query_params = parse_qs(parsed_url.query)
            return query_params.get('v', [None])[0]
        if parsed_url.path.startswith('/embed/'):
            return parsed_url.path.split('/')[2]
        if parsed_url.path.startswith('/v/'):
            return parsed_url.path.split('/')[2]
            
    return None

def extract_bilibili_bvid(url: str) -> str:
    """
    从B站视频URL中提取BVID
    支持格式:
    - https://www.bilibili.com/video/BV1xx411c7XZ
    - https://b23.tv/xxxxx (短链接需要重定向)
    """
    parsed_url = urlparse(url)
    
    if 'bilibili.com' in parsed_url.hostname:
        # 匹配 /video/BV...
        match = re.search(r'/video/(BV\w+)', parsed_url.path)
        if match:
            return match.group(1)
    
    return None

def extract_bilibili_uid(url: str) -> str:
    """
    从B站用户主页URL中提取UID
    支持格式:
    - https://space.bilibili.com/1234567
    - https://space.bilibili.com/1234567/video
    """
    parsed_url = urlparse(url)
    
    if 'space.bilibili.com' in parsed_url.hostname or parsed_url.hostname == 'space.bilibili.com':
        # 匹配 space.bilibili.com/数字
        match = re.search(r'/(\d+)', parsed_url.path)
        if match:
            return match.group(1)
    
    return None
