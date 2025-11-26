export const zh = {
    title: "AI 创作者风格分析",
    heroTitle: "解码任意",
    heroSubtitle: {
        youtube: "YouTuber 的风格",
        bilibili: "B站UP主 的风格",
    },
    heroDesc: {
        youtube: "输入频道链接，揭示其内容策略、脚本结构和爆款秘密。由多模态 AI 驱动。",
        bilibili: "输入主页链接，揭示其内容策略、脚本结构和爆款秘密。由多模态 AI 驱动。",
    },
    inputPlaceholder: {
        youtube: "粘贴 YouTube 频道链接 (例如: https://www.youtube.com/@Geekerwan)",
        bilibili: "粘贴 B站 UP主主页链接 (例如: https://space.bilibili.com/20259914)",
    },
    analyzeBtn: "开始分析",
    analyzingBtn: "分析中...",
    status: {
        ready: "准备就绪",
        initializing: "正在初始化...",
        fetching: "正在获取频道元数据...",
        extracting: "正在提取近期视频...",
        downloading: "正在下载字幕与评论...",
        analyzing_visual: "正在分析视觉风格...",
        generating: "正在生成 AI 报告...",
        complete: "分析完成！",
        error: "出错了",
    },
    waitMessage: "深度分析可能需要60秒，请耐心等待。",
    copy: "复制",
    copied: "JSON已复制",
};

export const en = {
    title: "AI Creator's Style Analysis",
    heroTitle: "Decode Any",
    heroSubtitle: {
        youtube: "YouTuber's Style",
        bilibili: "Bilibili Creator's Style",
    },
    heroDesc: {
        youtube: "Enter a channel URL to uncover their content strategy, script structure, and viral secrets. Powered by Multimodal AI.",
        bilibili: "Enter a user page URL to uncover their content strategy, script structure, and viral secrets. Powered by Multimodal AI.",
    },
    inputPlaceholder: {
        youtube: "Paste YouTube Channel URL (e.g., https://www.youtube.com/@Geekerwan)",
        bilibili: "Paste Bilibili User Page URL (e.g., https://space.bilibili.com/20259914)",
    },
    analyzeBtn: "Analyze",
    analyzingBtn: "Analyzing...",
    status: {
        ready: "Ready",
        initializing: "Initializing...",
        fetching: "Fetching channel metadata...",
        extracting: "Extracting recent videos...",
        downloading: "Downloading transcripts & comments...",
        analyzing_visual: "Analyzing visual style...",
        generating: "Generating AI report...",
        complete: "Complete!",
        error: "Error",
    },
    waitMessage: "This may take up to 60 seconds for deep analysis.",
    copy: "Copy",
    copied: "JSON Copied",
};

export type LocaleType = typeof zh;
