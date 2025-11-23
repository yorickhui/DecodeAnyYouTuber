# 🚀 DecodeAnyYouTuber 部署指南

本项目采用**前后端分离部署**策略:
- **前端 (Next.js)** → Vercel
- **后端 (FastAPI)** → Railway

---

## 📋 部署前准备

### 1. 准备API密钥
确保您有以下API密钥:
- `GEMINI_API_KEY` (Google Gemini API)
- `KIMI_API_KEY` (Moonshot AI,可选)

---

## 🔧 第一步:部署后端到Railway

### 1.1 注册Railway账号
1. 访问 [railway.app](https://railway.app)
2. 使用GitHub账号登录

### 1.2 创建新项目
1. 点击 **"New Project"**
2. 选择 **"Deploy from GitHub repo"**
3. 选择仓库: `yorickhui/DecodeAnyYouTuber`
4. Railway会自动检测到Python项目

**⚠️ 如果遇到"Nixpacks build failed"错误**:
- 原因: Railway无法自动检测到backend目录中的Python项目
- 解决: 项目已包含`nixpacks.toml`配置文件,重新部署即可
- 操作: 在Railway中点击 **"Redeploy"** 按钮

### 1.3 配置环境变量
在Railway项目设置中,添加以下环境变量:

```
GEMINI_API_KEY=你的Gemini API密钥
KIMI_API_KEY=你的Kimi API密钥(可选)
PORT=8000
```

**重要提示**:
- 点击项目 → **Variables** 标签页
- 点击 **"New Variable"** 添加每个变量
- 添加完成后点击 **"Deploy"**

### 1.4 获取后端URL
部署成功后:
1. 进入项目 → **Settings** → **Networking**
2. 点击 **"Generate Domain"** 生成公开域名
3. 复制生成的URL(格式: `https://xxx.railway.app`)
4. **保存这个URL**,稍后配置前端时需要用到

### 1.5 验证后端部署
访问: `https://你的域名.railway.app/docs`
应该能看到FastAPI的Swagger文档界面

---

## 🎨 第二步:部署前端到Vercel

### 2.1 注册Vercel账号
1. 访问 [vercel.com](https://vercel.com)
2. 使用GitHub账号登录

### 2.2 导入项目
1. 点击 **"Add New..."** → **"Project"**
2. 选择仓库: `yorickhui/DecodeAnyYouTuber`
3. 点击 **"Import"**

### 2.3 配置项目设置

#### Framework Preset
- 自动检测为 **Next.js** ✅

#### Root Directory
- 点击 **"Edit"**
- 选择 `frontend` 目录
- 点击 **"Continue"**

#### Build and Output Settings
保持默认:
- Build Command: `next build`
- Output Directory: `.next`
- Install Command: `npm install`

### 2.4 配置环境变量 ⭐ 重要
在 **Environment Variables** 部分添加:

| Name | Value |
|------|-------|
| `NEXT_PUBLIC_API_URL` | `https://你的Railway域名.railway.app` |

**示例**:
```
NEXT_PUBLIC_API_URL=https://decodeanyyoutuber-production.railway.app
```

### 2.5 部署
1. 点击 **"Deploy"**
2. 等待构建完成(约2-3分钟)
3. 部署成功后会显示预览链接

### 2.6 获取前端URL
部署成功后:
- Vercel会自动分配域名: `https://xxx.vercel.app`
- 您也可以在 **Settings** → **Domains** 中添加自定义域名

---

## 🔄 第三步:更新后端CORS配置

### 3.1 获取Vercel域名
复制您的Vercel项目域名,例如:
```
https://decode-any-you-tuber.vercel.app
```

### 3.2 更新backend/main.py
在本地项目中,打开 `backend/main.py`,找到CORS配置部分,将:
```python
"https://decode-any-you-tuber.vercel.app"  # Your production domain (update this)
```
替换为您的实际Vercel域名

### 3.3 提交并推送
```bash
git add backend/main.py
git commit -m "Update CORS for production domain"
git push origin main
```

Railway会自动重新部署后端

---

## ✅ 第四步:验证部署

### 4.1 测试后端
访问: `https://你的Railway域名.railway.app/docs`
- 应该能看到API文档
- 测试 `/` 端点,应该返回欢迎消息

### 4.2 测试前端
访问: `https://你的Vercel域名.vercel.app`
- 输入YouTube频道URL
- 点击分析按钮
- 检查是否能正常调用后端API

### 4.3 检查浏览器控制台
按 F12 打开开发者工具:
- 检查 **Console** 是否有CORS错误
- 检查 **Network** 标签页,API请求是否成功

---

## 🐛 常见问题排查

### 问题1: CORS错误
**症状**: 浏览器控制台显示 `Access-Control-Allow-Origin` 错误

**解决**:
1. 确认 `backend/main.py` 中的CORS配置包含您的Vercel域名
2. 重新部署后端

### 问题2: API请求失败
**症状**: 前端显示 "Failed to fetch" 或 500错误

**解决**:
1. 检查Railway后端日志: 项目 → **Deployments** → 点击最新部署 → **View Logs**
2. 确认环境变量 `GEMINI_API_KEY` 已正确设置
3. 检查Vercel环境变量 `NEXT_PUBLIC_API_URL` 是否正确

### 问题3: Railway部署失败
**症状**: 构建过程中出错

**解决**:
1. 检查 `backend/requirements.txt` 是否正确
2. 查看构建日志,找到具体错误信息
3. 确认 `runtime.txt` 指定的Python版本正确

### 问题4: 后端超时
**症状**: 分析请求超过30秒后失败

**解决**:
Railway免费版有请求时长限制,考虑:
1. 减少分析的视频数量(默认3个)
2. 优化代码性能
3. 升级Railway付费计划

---

## 💰 费用说明

### Railway
- **免费额度**: $5/月
- **超出后**: 按使用量计费
- **预估**: 轻度使用完全免费

### Vercel
- **免费额度**: 
  - 100GB带宽/月
  - 无限部署
- **超出后**: 按使用量计费
- **预估**: 个人项目完全免费

---

## 🔐 安全建议

1. **不要将API密钥提交到Git**
   - 已在 `.gitignore` 中排除 `mcp_config.json`
   - 仅在Railway/Vercel环境变量中配置

2. **定期轮换API密钥**
   - 每3-6个月更换一次

3. **监控使用量**
   - 定期检查Railway和Vercel的使用情况
   - 设置使用量告警

---

## 📚 相关文档

- [Railway文档](https://docs.railway.app)
- [Vercel文档](https://vercel.com/docs)
- [Next.js部署指南](https://nextjs.org/docs/deployment)
- [FastAPI部署指南](https://fastapi.tiangolo.com/deployment/)

---

## 🎉 完成!

恭喜!您的项目现已部署到生产环境。

**前端地址**: `https://你的项目.vercel.app`  
**后端地址**: `https://你的项目.railway.app`

如有问题,请查看上方的故障排查部分。
