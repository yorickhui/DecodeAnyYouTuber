export const zh = {
    title: "AI 频道风格分析",
    heroTitle: "解码任意",
    heroSubtitle: "YouTuber 的风格",
    heroDesc: "输入频道链接，揭示其内容策略、脚本结构和爆款秘密。由多模态 AI 驱动。",
    inputPlaceholder: "粘贴 YouTube 频道链接 (例如: https://www.youtube.com/@Geekerwan)",
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
    waitMessage: "深度分析可能需要 60 秒，请耐心等待。",
    copy: "复制",
    copied: "JSON已复制",
};

export const en = {
    title: "AI Channel Analysis",
    heroTitle: "Decode Any",
    heroSubtitle: "YouTuber's Style",
    heroDesc: "Enter a channel URL to uncover their content strategy, script structure, and viral secrets. Powered by Multimodal AI.",
    inputPlaceholder: "Paste YouTube Channel URL (e.g., https://www.youtube.com/@Geekerwan)",
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
