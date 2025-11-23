import os
import json
import base64
import logging
from typing import Dict, List, Any, Optional
import google.generativeai as genai
from openai import OpenAI
from .vision_service import VisionService
from utils.prompts import (
    CHANNEL_SYSTEM_PROMPT_ZH, 
    CHANNEL_SYSTEM_PROMPT_EN,
    CHANNEL_USER_PROMPT_TEMPLATE_ZH,
    CHANNEL_USER_PROMPT_TEMPLATE_EN
)

logger = logging.getLogger(__name__)

class AnalysisService:
    def __init__(self):
        # 初始化 Gemini (Google)
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        if self.gemini_key:
            genai.configure(api_key=self.gemini_key)
            self.model_gemini = genai.GenerativeModel('gemini-2.5-flash')
        
        # 初始化通义千问 VL (阿里云)
        self.qwen_key = os.getenv("QWEN_API_KEY")
        if self.qwen_key:
            self.client_qwen = OpenAI(
                api_key=self.qwen_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            )

    def _encode_image_base64(self, image_path: str) -> str:
        """将本地图片编码为 base64 格式"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def _analyze_with_gemini(self, system_prompt: str, prompt_text: str, thumbnails: List[str], language: str = "zh") -> Dict[str, Any]:
        """使用 Gemini 进行多模态分析"""
        logger.info("Using Gemini for channel analysis...")
        content_parts = [system_prompt, prompt_text]
        
        # 添加缩略图
        for thumb_path in thumbnails:
            if os.path.exists(thumb_path):
                img = genai.upload_file(thumb_path)
                content_parts.append(img)
        if thumbnails:
            # 根据语言选择提示文本
            thumbnail_prompt = (
                "以上是该频道最近视频的封面图 (Thumbnails),请分析其视觉风格一致性。" 
                if language == "zh" 
                else "Above are the thumbnails of recent videos from this channel. Please analyze their visual style consistency."
            )
            content_parts.append(thumbnail_prompt)

        response = self.model_gemini.generate_content(
            content_parts,
            generation_config={"response_mime_type": "application/json"},
            request_options={"timeout": 600}
        )
        
        return json.loads(response.text)

    def _analyze_with_qwen(self, system_prompt: str, prompt_text: str, thumbnails: List[str], language: str = "zh") -> Dict[str, Any]:
        """使用通义千问 VL 进行多模态分析"""
        logger.info("Using Qwen VL for channel analysis...")
        
        # 构建消息列表
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # 构建用户消息内容 (支持多模态)
        user_content = [
            {"type": "text", "text": prompt_text}
        ]
        
        # 添加缩略图 (base64 编码)
        for thumb_path in thumbnails:
            if os.path.exists(thumb_path):
                base64_image = self._encode_image_base64(thumb_path)
                # 获取图片扩展名
                ext = os.path.splitext(thumb_path)[1].lower()
                mime_type = {
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.png': 'image/png',
                    '.webp': 'image/webp'
                }.get(ext, 'image/jpeg')
                
                user_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime_type};base64,{base64_image}"
                    }
                })
        
        if thumbnails:
            # 根据语言选择提示文本
            thumbnail_prompt = (
                "以上是该频道最近视频的封面图 (Thumbnails),请分析其视觉风格一致性。" 
                if language == "zh" 
                else "Above are the thumbnails of recent videos from this channel. Please analyze their visual style consistency."
            )
            user_content.append({
                "type": "text",
                "text": thumbnail_prompt
            })
        
        messages.append({"role": "user", "content": user_content})
        
        # 调用通义千问 API
        response = self.client_qwen.chat.completions.create(
            model="qwen-vl-plus",
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.3,
        )
        
        content = response.choices[0].message.content
        return json.loads(content)

    def analyze_channel(self, 
                        recent_videos: List[Dict], 
                        detailed_videos: List[Dict],
                        thumbnails: List[str],
                        language: str = "zh") -> Dict[str, Any]:
        """
        根据语言环境智能选择模型进行频道风格分析
        - 中文环境: 主模型=通义千问 VL, 备用=Gemini
        - 英文环境: 主模型=Gemini, 备用=通义千问 VL
        """
        
        # 1. 准备视频摘要
        videos_summary_str = ""
        for v in recent_videos:
            videos_summary_str += f"- Title: {v.get('title')}, Views: {v.get('view_count')}, Date: {v.get('upload_date')}\n"

        # 2. 准备详细数据 (转录、评论、元数据)
        detailed_data_str = ""
        for v in detailed_videos:
            detailed_data_str += f"\n--- Video: {v.get('title')} ---\n"
            detailed_data_str += f"Description: {(v.get('description') or '')[:500]}...\n"
            detailed_data_str += f"Transcript Snippet: {v.get('transcript', '')[:2000]}...\n"
            detailed_data_str += f"Top Comments: {json.dumps(v.get('comments', [])[:10], ensure_ascii=False)}\n"

        # 3. 构建提示词
        if language == "en":
            system_prompt = CHANNEL_SYSTEM_PROMPT_EN
            user_prompt_template = CHANNEL_USER_PROMPT_TEMPLATE_EN
        else:
            system_prompt = CHANNEL_SYSTEM_PROMPT_ZH
            user_prompt_template = CHANNEL_USER_PROMPT_TEMPLATE_ZH

        prompt_text = user_prompt_template.format(
            videos_summary=videos_summary_str,
            detailed_data=detailed_data_str
        )

        # 4. 根据语言环境选择主备模型
        if language == "zh":
            # 中文环境: 通义千问优先, Gemini 备用
            primary_model = "qwen"
            fallback_model = "gemini"
        else:
            # 英文环境: Gemini 优先, 通义千问备用
            primary_model = "gemini"
            fallback_model = "qwen"

        # 5. 尝试主模型
        try:
            if primary_model == "qwen" and self.qwen_key:
                return self._analyze_with_qwen(system_prompt, prompt_text, thumbnails, language)
            elif primary_model == "gemini" and self.gemini_key:
                return self._analyze_with_gemini(system_prompt, prompt_text, thumbnails, language)
        except Exception as e:
            logger.error(f"{primary_model.capitalize()} analysis failed: {e}")
            logger.info(f"Falling back to {fallback_model.capitalize()}...")

        # 6. 主模型失败,尝试备用模型
        try:
            if fallback_model == "qwen" and self.qwen_key:
                return self._analyze_with_qwen(system_prompt, prompt_text, thumbnails, language)
            elif fallback_model == "gemini" and self.gemini_key:
                return self._analyze_with_gemini(system_prompt, prompt_text, thumbnails, language)
        except Exception as e:
            logger.error(f"{fallback_model.capitalize()} analysis failed: {e}")

        # 7. 两个模型都失败
        raise Exception("无可用 LLM 进行分析或两者均失败 (No available LLM for analysis or both failed)")
