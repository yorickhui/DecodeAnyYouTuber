#!/bin/bash

# 一键部署脚本 - 微信云托管

echo "🚀 开始部署到微信云托管..."

# 检查是否安装了腾讯云CLI
if ! command -v tccli &> /dev/null; then
    echo "❌ 未安装腾讯云CLI，请先安装: https://cloud.tencent.com/document/product/440/34011"
    exit 1
fi

# 配置参数
SERVICE_NAME="decode-youtube-backend"
ENV_ID=""  # 替换为你的环境ID
REGION="ap-guangzhou"  # 根据你的环境选择区域

# 检查必要的环境变量
if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ 请设置 GEMINI_API_KEY 环境变量"
    exit 1
fi

echo "✅ 环境检查通过"

# 部署到微信云托管
echo "📦 开始部署服务..."
tccli tcb CreateCloudBaseRunServerVersion \
    --EnvId $ENV_ID \
    --ServerName $SERVICE_NAME \
    --UploadType package \
    --PackageName local://./ \
    --FlowRatio 100 \
    --Cpu 1 \
    --Mem 2 \
    --MinNum 0 \
    --MaxNum 5 \
    --PolicyType cpu \
    --PolicyThreshold 60 \
    --ContainerPort 8000 \
    --EnvParams "GEMINI_API_KEY=$GEMINI_API_KEY,QWEN_API_KEY=$QWEN_API_KEY" \
    --Region $REGION

echo "✅ 部署命令已发送！"
echo "📊 请在微信云托管控制台查看部署进度"
echo "🔗 控制台地址: https://cloud.weixin.qq.com/"
