import os
import json
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
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.kimi_key = os.getenv("KIMI_API_KEY")
        
        if self.gemini_key:
            genai.configure(api_key=self.gemini_key)
            # Reverting to "gemini-2.5-flash" for better performance/speed.
            # "gemini-3-pro-preview" was timing out consistently (>600s).
            self.model_gemini = genai.GenerativeModel('gemini-2.5-flash')
        
        if self.kimi_key:
            self.client_kimi = OpenAI(
                api_key=self.kimi_key,
                base_url="https://api.moonshot.cn/v1",
            )

    def analyze_channel(self, 
                        recent_videos: List[Dict], 
                        detailed_videos: List[Dict],
                        thumbnails: List[str],
                        language: str = "zh") -> Dict[str, Any]:
        """
        Analyzes channel style by aggregating data from multiple videos.
        """
        
        # 1. Prepare Summary of Recent Videos
        videos_summary_str = ""
        for v in recent_videos:
            videos_summary_str += f"- Title: {v.get('title')}, Views: {v.get('view_count')}, Date: {v.get('upload_date')}\n"

        # 2. Prepare Detailed Data (Transcripts, Comments, Metadata)
        detailed_data_str = ""
        for v in detailed_videos:
            detailed_data_str += f"\n--- Video: {v.get('title')} ---\n"
            detailed_data_str += f"Description: {(v.get('description') or '')[:500]}...\n"
            detailed_data_str += f"Transcript Snippet: {v.get('transcript', '')[:2000]}...\n" # Limit context
            detailed_data_str += f"Top Comments: {json.dumps(v.get('comments', [])[:10], ensure_ascii=False)}\n"

        # 3. Construct Prompt
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

        # 4. Call LLM (Gemini Preferred for Multimodal)
        if self.gemini_key:
            try:
                logger.info("Using Gemini for channel analysis...")
                content_parts = [system_prompt, prompt_text]
                
                # Add thumbnails
                for thumb_path in thumbnails:
                    if os.path.exists(thumb_path):
                        img = genai.upload_file(thumb_path)
                        content_parts.append(img)
                if thumbnails:
                    content_parts.append("以上是该频道最近视频的封面图 (Thumbnails)，请分析其视觉风格一致性。")

                response = self.model_gemini.generate_content(
                    content_parts,
                    generation_config={"response_mime_type": "application/json"},
                    request_options={"timeout": 600}
                )
                
                return json.loads(response.text)
            except Exception as e:
                logger.error(f"Gemini analysis failed: {e}")
                # Fallback to OpenAI (Text only)
        
        if self.kimi_key:
            try:
                logger.info("Using Kimi (Moonshot AI) for channel analysis (Text Only)...")
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt_text}
                ]
                
                response = self.client_kimi.chat.completions.create(
                    model="moonshot-v1-128k",
                    messages=messages,
                    response_format={"type": "json_object"},
                    temperature=0.3, # Lower temperature for more stable JSON
                )
                content = response.choices[0].message.content
                try:
                    return json.loads(content)
                except json.JSONDecodeError as e:
                    logger.warning(f"Kimi JSON Decode Error: {e}. Attempting to repair...")
                    try:
                        # Robust repair for truncated JSON
                        stack = []
                        in_string = False
                        escape = False
                        
                        for char in content:
                            if in_string:
                                if escape:
                                    escape = False
                                elif char == '\\':
                                    escape = True
                                elif char == '"':
                                    in_string = False
                            else:
                                if char == '"':
                                    in_string = True
                                elif char == '{':
                                    stack.append('}')
                                elif char == '[':
                                    stack.append(']')
                                elif char == '}' or char == ']':
                                    if stack:
                                        if stack[-1] == char:
                                            stack.pop()
                        
                        # If in string, close it
                        repaired_content = content
                        if in_string:
                            repaired_content += '"'
                        
                        # Close remaining stack in reverse order
                        while stack:
                            repaired_content += stack.pop()
                        
                        logger.info(f"Repaired JSON content: {repaired_content[-100:]}") # Log end of repaired content
                        return json.loads(repaired_content)
                    except Exception as repair_error:
                        logger.error(f"JSON Repair failed: {repair_error}")
                        logger.error(f"Raw Content: {content}")
                        raise e
            except Exception as e:
                logger.error(f"Kimi analysis failed: {e}")
                print(f"❌ Kimi analysis failed: {e}") # Force print to stdout
        
        raise Exception("No available LLM for analysis or both failed.")
