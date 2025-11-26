import os
import logging
import asyncio
from typing import Optional, Dict, List, Any

# Monkey patch bilibili_api to fix proxy/proxies parameter mismatch with httpx 0.23.3
import httpx
original_async_client_init = httpx.AsyncClient.__init__

def patched_async_client_init(self, *args, proxy=None, proxies=None, **kwargs):
    """修复bilibili_api传入proxy参数的问题，httpx 0.23.3需要proxies参数"""
    if proxy is not None and proxies is None:
        proxies = proxy
    original_async_client_init(self, *args, proxies=proxies, **kwargs)

httpx.AsyncClient.__init__ = patched_async_client_init

# 在导入bilibili_api之前设置不使用代理
import bilibili_api
from bilibili_api import request_settings
# 设置所有可能的代理相关参数
request_settings.set_proxy("")
request_settings.trust_env = False  # 不使用环境变量中的代理

from bilibili_api import user, video, Credential
from bilibili_api.exceptions import ResponseCodeException
from utils.helpers import extract_bilibili_bvid, extract_bilibili_uid

logger = logging.getLogger(__name__)

class BilibiliService:
    """
    B站数据提取服务
    提供与YouTubeService对等的功能,用于获取UP主视频数据
    """
    
    def __init__(self):
        """
        初始化B站服务
        可选: 从环境变量加载SESSDATA以解锁更多功能
        """
        # 可选的认证凭证(用于获取高清视频、部分API)
        sessdata = os.getenv("BILIBILI_SESSDATA", "")
        bili_jct = os.getenv("BILIBILI_BILI_JCT", "")
        buvid3 = os.getenv("BILIBILI_BUVID3", "")
        
        self.credential = None
        if sessdata and bili_jct and buvid3:
            self.credential = Credential(
                sessdata=sessdata,
                bili_jct=bili_jct,
                buvid3=buvid3
            )
            logger.info("Bilibili credential loaded")
        else:
            logger.info("Running Bilibili service without credential (limited features)")
    
    async def get_user_recent_videos(self, user_url: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        获取UP主最近的视频列表
        
        Args:
            user_url: UP主主页URL,例如 https://space.bilibili.com/1234567
            limit: 获取视频数量限制
            
        Returns:
            视频元数据列表,格式与YouTubeService统一
        """
        uid = extract_bilibili_uid(user_url)
        if not uid:
            raise ValueError(f"Invalid Bilibili user URL: {user_url}")
        
        logger.info(f"Fetching videos for Bilibili UID: {uid}")
        
        try:
            # 创建用户对象
            u = user.User(uid=int(uid), credential=self.credential)
            
            # 获取用户投稿视频
            videos_data = await u.get_videos(pn=1, ps=limit)  # pn=页码, ps=每页数量
            
            videos = []
            if videos_data and 'list' in videos_data and 'vlist' in videos_data['list']:
                for v in videos_data['list']['vlist'][:limit]:
                    videos.append({
                        "id": v.get("bvid"),
                        "title": v.get("title"),
                        "url": f"https://www.bilibili.com/video/{v.get('bvid')}",
                        "duration": v.get("length"),  # 格式: "MM:SS"
                        "view_count": v.get("play"),
                        "upload_date": v.get("created"),  # Unix timestamp
                        "description": v.get("description", ""),
                    })
            
            logger.info(f"Successfully fetched {len(videos)} videos")
            return videos
            
        except ResponseCodeException as e:
            logger.error(f"Bilibili API error: {e}")
            raise ValueError(f"Failed to fetch videos from Bilibili: {e}")
        except Exception as e:
            logger.error(f"Error fetching Bilibili videos: {e}")
            raise e
    
    async def get_video_details(self, video_url: str, fetch_comments: bool = True) -> Dict[str, Any]:
        """
        获取视频详细信息
        
        Args:
            video_url: 视频URL,例如 https://www.bilibili.com/video/BV1xx411c7XZ
            fetch_comments: 是否获取评论
            
        Returns:
            视频详情字典,格式与YouTubeService统一
        """
        bvid = extract_bilibili_bvid(video_url)
        if not bvid:
            raise ValueError(f"Invalid Bilibili video URL: {video_url}")
        
        logger.info(f"Fetching details for Bilibili video: {bvid}")
        
        try:
            # 创建视频对象
            v = video.Video(bvid=bvid, credential=self.credential)
            
            # 获取视频信息
            video_info = await v.get_info()
            
            # 获取视频统计数据
            stats = video_info.get('stat', {})
            
            # 获取评论(可选)
            comments = []
            if fetch_comments:
                try:
                    # 获取前20条评论
                    replies_data = await v.get_replies(page_index=1)
                    if replies_data and 'replies' in replies_data:
                        for reply in replies_data['replies'][:20]:
                            if 'content' in reply and 'message' in reply['content']:
                                comments.append(reply['content']['message'])
                except Exception as e:
                    logger.warning(f"Failed to fetch comments for {bvid}: {e}")
            
            # 标准化输出格式
            return {
                "id": bvid,
                "title": video_info.get("title"),
                "description": video_info.get("desc"),
                "view_count": stats.get("view"),
                "like_count": stats.get("like"),
                "coin_count": stats.get("coin"),  # B站特有: 投币数
                "favorite_count": stats.get("favorite"),  # B站特有: 收藏数
                "share_count": stats.get("share"),  # B站特有: 分享数
                "danmaku_count": stats.get("danmaku"),  # B站特有: 弹幕数
                "duration": video_info.get("duration"),  # 秒数
                "upload_date": video_info.get("pubdate"),  # Unix timestamp
                "uploader": video_info.get("owner", {}).get("name"),
                "channel_id": video_info.get("owner", {}).get("mid"),
                "tags": [tag.get("tag_name") for tag in video_info.get("tag", [])],
                "thumbnail": video_info.get("pic"),
                "categories": [video_info.get("tname", "")],  # 分区名称
                "comments": comments
            }
            
        except ResponseCodeException as e:
            logger.error(f"Bilibili API error for {bvid}: {e}")
            return {"id": bvid, "error": str(e)}
        except Exception as e:
            logger.error(f"Error fetching details for {bvid}: {e}")
            return {"id": bvid, "error": str(e)}
    
    async def get_subtitle(self, bvid: str) -> str:
        """
        获取视频字幕/字幕文本
        
        Args:
            bvid: 视频BVID
            
        Returns:
            完整字幕文本
        """
        if not bvid:
            return ""
        
        logger.info(f"Fetching subtitle for Bilibili video: {bvid}")
        
        try:
            v = video.Video(bvid=bvid, credential=self.credential)
            
            # 获取字幕列表
            subtitle_data = await v.get_subtitle()
            
            if not subtitle_data or 'subtitles' not in subtitle_data:
                logger.warning(f"No subtitles found for {bvid}")
                return ""
            
            # 优先选择中文字幕,然后是其他语言
            subtitle_url = None
            for sub in subtitle_data['subtitles']:
                lan = sub.get('lan', '')
                if lan in ['zh-CN', 'zh-Hans']:
                    subtitle_url = sub.get('subtitle_url')
                    break
            
            # 如果没有中文字幕,取第一个
            if not subtitle_url and subtitle_data['subtitles']:
                subtitle_url = subtitle_data['subtitles'][0].get('subtitle_url')
            
            if not subtitle_url:
                return ""
            
            # 下载字幕内容
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https:{subtitle_url}") as resp:
                    subtitle_json = await resp.json()
            
            # 拼接字幕文本
            if subtitle_json and 'body' in subtitle_json:
                full_text = " ".join([item.get('content', '') for item in subtitle_json['body']])
                return full_text
            
            return ""
            
        except Exception as e:
            logger.error(f"Error fetching subtitle for {bvid}: {e}")
            return ""
