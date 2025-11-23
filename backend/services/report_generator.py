import json
from typing import Dict, Any

class ReportGenerator:
    def generate_markdown_report(self, analysis_data: Dict[str, Any], language: str = "zh") -> str:
        """
        Generates a Markdown report from the channel analysis data (Framework v2.0).
        """
        # Helper to format list as bullet points
        def fmt_list(items):
            if not items:
                return "无" if language == "zh" else "None"
            return "\n".join([f"- {item}" for item in items])

        # Translation Dictionary
        t = {
            "zh": {
                "unknown_channel": "未知频道",
                "title_suffix": "创作风格分析报告",
                "platform": "平台",
                "framework": "分析框架",
                "section1": "1️⃣ 内容定位",
                "core_theme": "核心主题",
                "target_audience": "目标受众",
                "content_types": "内容类型",
                "value_proposition": "价值承诺",
                "section2": "2️⃣ 结构框架",
                "blueprint": "整体蓝图",
                "hook_type": "Hook类型",
                "mid_logic": "中段逻辑",
                "ending_style": "结尾风格",
                "section3": "3️⃣ 叙事与表达",
                "storytelling": "讲故事方式",
                "emotional_logical": "情绪/逻辑",
                "personality": "人格特征",
                "common_devices": "常用手法",
                "section4": "4️⃣ 语言风格",
                "sentence_style": "句式",
                "pace_info": "信息节奏",
                "tone_keywords": "语气关键词",
                "signature_phrases": "标志性短语",
                "section5": "5️⃣ 节奏与剪辑感",
                "rhythm": "整体节奏",
                "transition": "转场风格",
                "highlight": "高光时刻",
                "visual_audio": "视听提示",
                "section6": "6️⃣ 心理学抓手",
                "section7": "7️⃣ 可复用创作公式 ⭐",
                "core_formula": "核心公式",
                "steps": "实施步骤",
                "json_title": "📋 Creator Style JSON（可直接复制）",
                "json_desc": "> **一键复制，让 AI 精准复刻该频道风格：**\n>\n> 将下方 JSON 与你的选题一起输入给 AI，告诉 AI 按照此风格创作即可。AI 会自动模仿该创作者的结构、叙事、语气、节奏等。"
            },
            "en": {
                "unknown_channel": "Unknown Channel",
                "title_suffix": "Style Analysis Report",
                "platform": "Platform",
                "framework": "Analysis Framework",
                "section1": "1️⃣ Content Positioning",
                "core_theme": "Core Theme",
                "target_audience": "Target Audience",
                "content_types": "Content Types",
                "value_proposition": "Value Proposition",
                "section2": "2️⃣ Structure Pattern",
                "blueprint": "High-Level Structure",
                "hook_type": "Hook Types",
                "mid_logic": "Mid-Section Logic",
                "ending_style": "Ending Style",
                "section3": "3️⃣ Narrative & Expression",
                "storytelling": "Storytelling Approach",
                "emotional_logical": "Emotional vs Logical",
                "personality": "Personality Traits",
                "common_devices": "Common Devices",
                "section4": "4️⃣ Language Tone",
                "sentence_style": "Sentence Style",
                "pace_info": "Pace of Information",
                "tone_keywords": "Tone Keywords",
                "signature_phrases": "Signature Phrases",
                "section5": "5️⃣ Pacing & Editing",
                "rhythm": "Overall Rhythm",
                "transition": "Transition Style",
                "highlight": "Highlight Moments",
                "visual_audio": "Visual/Audio Cues",
                "section6": "6️⃣ Psychological Hooks",
                "section7": "7️⃣ Reusable Creation Formula ⭐",
                "core_formula": "Core Formula",
                "steps": "Implementation Steps",
                "json_title": "📋 Creator Style JSON (Copy Ready)",
                "json_desc": "> **One-Click Copy for AI Style Replication:**\n>\n> Feed the JSON below along with your topic to AI. It will automatically mimic the creator's structure, narrative, tone, and pacing."
            }
        }
        
        lang_dict = t.get(language, t["zh"])

        # Extract sections (v2.0 schema)
        creator_name = analysis_data.get("creator_name", lang_dict["unknown_channel"])
        platform_name = analysis_data.get("platform", "YouTube")
        
        positioning = analysis_data.get("content_positioning", {})
        structure = analysis_data.get("structure_pattern", {})
        narrative = analysis_data.get("narrative_style", {})
        language_style = analysis_data.get("language_tone", {})
        pacing = analysis_data.get("pacing_and_editing_cues", {})
        hooks = analysis_data.get("psychological_hooks", [])
        formula = analysis_data.get("reusable_creation_formula", {})

        report = f"""# 🎬 {creator_name} - {lang_dict['title_suffix']}

**{lang_dict['platform']}**: {platform_name}  
**{lang_dict['framework']}**: Creator Style Analysis Framework v2.0

---

## {lang_dict['section1']}

- **{lang_dict['core_theme']}**: {positioning.get('core_theme', 'N/A')}
- **{lang_dict['target_audience']}**: {positioning.get('target_audience', 'N/A')}
- **{lang_dict['content_types']}**: {', '.join(positioning.get('content_types', []))}
- **{lang_dict['value_proposition']}**: {positioning.get('value_proposition', 'N/A')}

---

## {lang_dict['section2']}

**{lang_dict['blueprint']}**: {structure.get('high_level_structure', 'N/A')}

- **{lang_dict['hook_type']}**: {', '.join(structure.get('hook_types', []))}
- **{lang_dict['mid_logic']}**: {structure.get('mid_section_logic', 'N/A')}
- **{lang_dict['ending_style']}**: {structure.get('ending_style', 'N/A')}

---

## {lang_dict['section3']}

- **{lang_dict['storytelling']}**: {narrative.get('storytelling_approach', 'N/A')}
- **{lang_dict['emotional_logical']}**: {narrative.get('emotional_vs_logical', 'N/A')}
- **{lang_dict['personality']}**: {narrative.get('personality_traits', 'N/A')}
- **{lang_dict['common_devices']}**:
{fmt_list(narrative.get('common_devices', []))}

---

## {lang_dict['section4']}

**{lang_dict['sentence_style']}**: {language_style.get('sentence_style', 'N/A')}  
**{lang_dict['pace_info']}**: {language_style.get('pace_of_information', 'N/A')}

- **{lang_dict['tone_keywords']}**: {', '.join(language_style.get('tone_keywords', []))}
- **{lang_dict['signature_phrases']}**:
{fmt_list(language_style.get('signature_phrases', []))}

---

## {lang_dict['section5']}

- **{lang_dict['rhythm']}**: {pacing.get('video_rhythm', 'N/A')}
- **{lang_dict['transition']}**: {pacing.get('transition_style', 'N/A')}
- **{lang_dict['highlight']}**: {pacing.get('highlight_moments', 'N/A')}
- **{lang_dict['visual_audio']}**:
{fmt_list(pacing.get('visual_or_audio_cues', []))}

---

## {lang_dict['section6']}

{fmt_list(hooks)}

---

## {lang_dict['section7']}

**{lang_dict['core_formula']}**: {formula.get('one_line_formula', 'N/A')}

**{lang_dict['steps']}**:
{fmt_list(formula.get('steps', []))}

---

## {lang_dict['json_title']}

{lang_dict['json_desc']}

```json
{json.dumps(analysis_data, ensure_ascii=False, indent=2)}
```
"""
        return report
