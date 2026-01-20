#!/bin/bash
set -e

echo "=== Render 启动脚本 ==="
echo "当前目录: $(pwd)"
echo "Python 版本: $(python --version)"

# 检查是否有旧的虚拟环境
if [ -d ".venv" ]; then
    echo "发现旧的虚拟环境，正在删除..."
    rm -rf .venv
fi

# 检查 coze_coding_dev_sdk 版本
if [ -f ".venv/lib/python3.11/site-packages/coze_coding_dev_sdk/core/client.py" ]; then
    echo "警告：发现旧的 coze_coding_dev_sdk 安装"
    echo "尝试重新安装..."
    pip uninstall -y coze-coding-dev-sdk || true
fi

# 重新安装所有依赖
echo "正在安装依赖..."
pip install --no-cache-dir --force-reinstall --upgrade --ignore-installed -r requirements-render.txt

# 验证关键依赖版本
echo "验证 coze_coding_dev_sdk 版本..."
pip show coze-coding-dev-sdk | grep Version

# 启动应用
echo "启动 Web 服务..."
python src/web/app.py
