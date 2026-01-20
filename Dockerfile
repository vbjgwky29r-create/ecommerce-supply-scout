# 使用 Python 3.11.11 作为基础镜像
FROM python:3.11.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 验证关键依赖版本
RUN pip show coze-coding-dev-sdk | grep Version

# 复制应用代码
COPY . .

# 创建必要的目录
RUN mkdir -p /tmp

# 设置环境变量
ENV FLASK_SECRET_KEY=ecommerce-agent-secret-key-2024
ENV COZE_WORKLOAD_IDENTITY_API_KEY=e863036f-fe71-4771-9510-9a5d329d65c8
ENV PORT=5000

# 暴露端口
EXPOSE 5000

# 启动应用
CMD ["python", "src/web/app.py"]
