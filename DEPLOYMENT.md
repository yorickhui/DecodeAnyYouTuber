# 🚀 DecodeAnyYouTuber 部署指南

本项目采用**前后端分离部署**策略:
- **前端 (Next.js)** → Vercel
- **后端 (FastAPI)** → Railway

---

## 📋 部署前准备

### 1. 准备API密钥
确保您有以下API密钥:
- `GEMINI_API_KEY` (Google Gemini API)
- `QWEN_API_KEY` (阿里云通义千问,可选)

**模型选择策略**:
- 中文环境:优先使用通义千问 VL,Gemini 作为备用
- 英文环境:优先使用 Gemini,通义千问 VL 作为备用
- 两个模型都支持多模态分析(文本+图片)

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
QWEN_API_KEY=你的通义千问API密钥(可选)
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

---

## 📖 部署实战经验教训

### 🔥 关键问题与解决方案

#### 1. Railway Python环境配置问题

**遇到的问题**:
- Nixpacks无法自动检测backend子目录中的Python项目
- 自定义nixpacks.toml导致pip模块缺失
- Nix环境的"externally-managed"限制

**最终解决方案**:
✅ **将requirements.txt复制到项目根目录**
- Railway会自动检测根目录的requirements.txt
- 使用默认Python buildpack,避免Nix环境复杂性
- 在railway.json中只配置启动命令

**经验教训**:
> 💡 对于简单的Python项目,使用Railway的默认检测机制比自定义配置更可靠

---

#### 2. OpenCV依赖问题

**遇到的问题**:
```
ImportError: libGL.so.1: cannot open shared object file: No such file or directory
```

**尝试的方案**:
- ❌ 创建Aptfile添加系统库 (在默认buildpack中不生效)
- ❌ 使用nixpacks.toml配置系统包 (太复杂)

**最终解决方案**:
✅ **使用opencv-python-headless替代opencv-python**

```diff
- opencv-python
+ opencv-python-headless
```

**优势**:
- 无需GUI库依赖(libGL, libGLU等)
- 体积更小(减少约100MB)
- 功能完整,适合服务器环境
- 部署更快,更稳定

**经验教训**:
> 💡 服务器环境优先选择headless版本的库,避免不必要的GUI依赖

---

#### 3. CORS配置陷阱

**遇到的问题**:
```
Access-Control-Allow-Origin header is not present
```

**错误配置**:
```python
allow_origins=["https://*.vercel.app"]  # ❌ 通配符不起作用
```

**问题分析**:
- Vercel的预览部署域名格式: `https://project-xxx-user.vercel.app`
- CORS的`allow_origins`不支持通配符`*`
- 每次预览部署域名都不同

**最终解决方案**:
✅ **使用allow_origin_regex支持正则表达式**

```python
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*\.vercel\.app|http://localhost:\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**匹配规则**:
- `https://.*\.vercel\.app` - 所有Vercel域名(包括预览)
- `http://localhost:\d+` - 本地开发任意端口
- `https://your-domain\.vercel\.app` - 生产域名

**经验教训**:
> 💡 对于动态子域名,使用正则表达式而非通配符配置CORS

---

#### 4. Vercel环境变量配置错误

**遇到的问题**:
```
Request URL: https://frontend.vercel.app/backend.railway.app/api
```

**错误配置**:
```
NEXT_PUBLIC_API_URL=backend.railway.app  # ❌ 缺少协议
```

**问题分析**:
- 前端代码使用模板字符串拼接URL
- 缺少`https://`导致被当作相对路径
- 结果拼接成错误的URL

**正确配置**:
```
NEXT_PUBLIC_API_URL=https://backend.railway.app  # ✅ 包含完整协议
```

**经验教训**:
> 💡 环境变量中的URL必须包含完整的协议(https://)

---

### 🎯 最佳实践总结

#### Railway后端部署

1. **项目结构**
   ```
   项目根目录/
   ├── requirements.txt      # ✅ 必须在根目录
   ├── runtime.txt          # 可选,指定Python版本
   ├── railway.json         # 只配置启动命令
   └── backend/
       ├── main.py
       └── requirements.txt  # 保留用于本地开发
   ```

2. **依赖选择**
   - 优先使用headless/server版本的库
   - 避免GUI依赖(opencv, matplotlib等)
   - 使用轻量级替代方案

3. **环境变量**
   - 在Railway Variables中配置
   - 不要在代码中硬编码
   - 敏感信息只存在环境变量中

#### Vercel前端部署

1. **Root Directory配置**
   - 必须选择`frontend`目录
   - 否则会找不到package.json

2. **环境变量**
   - 名称必须以`NEXT_PUBLIC_`开头才能在客户端访问
   - 值必须包含完整URL(含协议)
   - 修改后需要重新部署

3. **重新部署触发**
   - 环境变量更新后不会自动部署
   - 需要手动Redeploy或推送新commit

#### CORS配置

1. **开发环境**
   ```python
   allow_origin_regex=r"http://localhost:\d+"
   ```

2. **生产环境**
   ```python
   allow_origin_regex=r"https://.*\.vercel\.app"
   ```

3. **组合配置**
   ```python
   allow_origin_regex=r"https://.*\.vercel\.app|http://localhost:\d+"
   ```

---

### ⚡ 部署流程优化建议

#### 推荐部署顺序

1. **先部署后端** (Railway)
   - 获取后端URL
   - 验证API正常工作
   - 配置好环境变量

2. **再部署前端** (Vercel)
   - 使用后端URL配置环境变量
   - 选择正确的Root Directory
   - 验证前后端连接

3. **最后调整CORS**
   - 获取前端域名
   - 更新后端CORS配置
   - 推送代码触发重新部署

#### 调试技巧

1. **Railway日志查看**
   ```
   Deployments → 点击部署 → View Logs
   ```

2. **Vercel日志查看**
   ```
   Deployments → 点击部署 → Build Logs / Runtime Logs
   ```

3. **浏览器调试**
   ```
   F12 → Console (查看错误)
   F12 → Network (查看请求)
   ```

---

### 🚨 常见错误速查表

| 错误信息 | 原因 | 解决方案 |
|---------|------|---------|
| `Nixpacks build failed` | 未检测到Python项目 | requirements.txt放根目录 |
| `libGL.so.1: cannot open` | OpenCV缺少GUI库 | 使用opencv-python-headless |
| `CORS policy` | 域名不在白名单 | 使用allow_origin_regex |
| `Failed to fetch` | API URL配置错误 | 检查NEXT_PUBLIC_API_URL |
| `Unexpected end of JSON` | 请求失败返回空响应 | 检查后端是否运行 |
| `405 Method Not Allowed` | URL拼接错误 | 环境变量加https:// |

---

### 💡 性能优化建议

1. **减少依赖体积**
   - 使用headless版本库
   - 移除不必要的依赖
   - 考虑使用CDN

2. **优化API响应**
   - 限制分析视频数量
   - 实现结果缓存
   - 使用流式响应

3. **监控和告警**
   - 设置Railway使用量告警
   - 监控Vercel带宽使用
   - 记录错误日志

---

## 🎓 总结

通过本次部署,我们学到:

1. ✅ **简单优于复杂** - 使用平台默认配置比自定义更可靠
2. ✅ **选择合适的库** - 服务器环境使用headless版本
3. ✅ **正则表达式** - CORS配置支持动态域名
4. ✅ **完整的URL** - 环境变量必须包含协议
5. ✅ **逐步验证** - 先后端后前端,分步调试

**部署不是一次性的,而是持续优化的过程!** 🚀
