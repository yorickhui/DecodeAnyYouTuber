# 使用Python 3.11官方镜像（基于Debian bookworm稳定版）
FROM python:3.11-slim-bookworm

# 设置时区和环境变量
ENV TZ=Asia/Shanghai \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# 安装系统依赖（精简版，opencv-python-headless不需要图形库）
RUN apt-get update && apt-get install -y --no-install-recommends \
    tzdata \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && ln -sf /usr/share/zoneinfo/${TZ} /etc/localtime \
    && echo ${TZ} > /etc/timezone

# 设置工作目录
WORKDIR /app

# 配置pip使用腾讯云镜像源（加速构建）
RUN pip config set global.index-url https://mirrors.tencent.com/pypi/simple

# 复制依赖文件并安装Python包
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY backend/ ./backend/
COPY run.sh .

# 赋予执行权限
RUN chmod +x run.sh

# 暴露端口
EXPOSE 8000

# 启动命令（使用PORT环境变量）
CMD ["sh", "-c", "cd backend && uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
