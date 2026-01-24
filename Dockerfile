# 使用 Python 3.11.11 作为基础镜像
FROM python:3.11.11-slim

# 构建版本号ARG（每次修改依赖时递增，强制清除Docker缓存）
# 强制安装 coze-coding-dev-sdk==0.5.3 修复 f-string 语法错误（根本性解决方案）
# 修复配置文件路径问题
ARG BUILD_VERSION=2025-01-24-v26
ENV BUILD_VERSION=${BUILD_VERSION}

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

# 强制安装正确版本的关键依赖（覆盖 requirements.txt 中的版本）
RUN pip install --no-cache-dir --force-reinstall \
    coze-coding-dev-sdk==0.5.3

# 验证关键依赖版本
RUN pip show coze-coding-dev-sdk | grep Version

# 复制应用代码
COPY . .

# 创建必要的目录
RUN mkdir -p /tmp /app/config

# 确保 config 目录存在并包含配置文件
RUN if [ ! -f /app/config/agent_llm_config.json ]; then echo "Error: config/agent_llm_config.json not found"; exit 1; fi

# 设置环境变量
ENV FLASK_SECRET_KEY=ecommerce-agent-secret-key-2024
ENV COZE_WORKLOAD_IDENTITY_API_KEY=e863036f-fe71-4771-9510-9a5d329d65c8
ENV PORT=5000

# 暴露端口
EXPOSE 5000

# 启动应用
CMD ["python", "src/web/app.py"]
