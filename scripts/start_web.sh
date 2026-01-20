#!/bin/bash

# 启动电商货源猎手 Web 服务

echo "=========================================="
echo "  电商货源猎手 Web 服务启动脚本"
echo "=========================================="

# 检查是否在项目根目录
if [ ! -f "requirements.txt" ]; then
    echo "错误: 请在项目根目录下运行此脚本"
    exit 1
fi

# 设置工作目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

echo ""
echo "📂 工作目录: $PROJECT_DIR"
echo ""

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3"
    exit 1
fi

echo "✅ Python版本: $(python3 --version)"
echo ""

# 检查并安装依赖
echo "📦 检查依赖..."
if ! python3 -c "import flask" 2>/dev/null; then
    echo "正在安装Flask依赖..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "错误: 依赖安装失败"
        exit 1
    fi
    echo "✅ 依赖安装成功"
else
    echo "✅ 依赖已安装"
fi

echo ""

# 设置环境变量
export PYTHONPATH="${PROJECT_DIR}:${PROJECT_DIR}/src:${PYTHONPATH}"
export FLASK_SECRET_KEY="${FLASK_SECRET_KEY:-ecommerce-agent-secret-key-2024}"
export WEB_HOST="${WEB_HOST:-0.0.0.0}"
export WEB_PORT="${WEB_PORT:-5000}"
export WEB_DEBUG="${WEB_DEBUG:-False}"

echo "⚙️  配置信息:"
echo "   - 主机: ${WEB_HOST}"
echo "   - 端口: ${WEB_PORT}"
echo "   - 调试模式: ${WEB_DEBUG}"
echo ""

# 检查端口是否被占用
if command -v lsof &> /dev/null; then
    if lsof -Pi :${WEB_PORT} -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "⚠️  警告: 端口 ${WEB_PORT} 已被占用"
        read -p "是否要继续? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "取消启动"
            exit 0
        fi
    fi
fi

echo ""
echo "🚀 启动Web服务..."
echo ""
echo "访问地址:"
echo "   - 本地: http://localhost:${WEB_PORT}"
echo "   - 局域网: http://$(hostname -I | awk '{print $1}'):${WEB_PORT}"
echo ""
echo "在微信中访问: 将上面的URL发送到微信，点击即可打开"
echo ""
echo "按 Ctrl+C 停止服务"
echo "=========================================="
echo ""

# 启动服务
cd src/web
python3 app.py
