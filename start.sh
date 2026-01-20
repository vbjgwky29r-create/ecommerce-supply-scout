#!/bin/bash
set -e

echo "=== 应用启动前的强制修复脚本 ==="

# 检测虚拟环境路径
if [ -d ".venv" ]; then
    echo "发现虚拟环境: .venv"
    VENV_PATH=".venv"
elif [ -d "/opt/render/project/src/.venv" ]; then
    echo "发现虚拟环境: /opt/render/project/src/.venv"
    VENV_PATH="/opt/render/project/src/.venv"
else
    echo "未找到虚拟环境，使用系统 Python"
    VENV_PATH=""
fi

if [ -n "$VENV_PATH" ]; then
    # 检查 coze_coding_dev_sdk 版本
    echo "检查 coze_coding_dev_sdk 版本..."
    VERSION=$($VENV_PATH/bin/pip show coze-coding-dev-sdk 2>/dev/null | grep Version | awk '{print $2}')

    if [ "$VERSION" = "0.5.5" ]; then
        echo "❌ 发现错误版本: 0.5.5，正在修复..."

        # 强制卸载
        $VENV_PATH/bin/pip uninstall -y coze-coding-dev-sdk

        # 强制安装正确版本
        $VENV_PATH/bin/pip install --no-cache-dir --force-reinstall coze-coding-dev-sdk==0.5.4

        # 验证
        NEW_VERSION=$($VENV_PATH/bin/pip show coze-coding-dev-sdk | grep Version | awk '{print $2}')
        echo "✅ 已修复为版本: $NEW_VERSION"
    else
        echo "✅ 版本正确: $VERSION"
    fi

    # 启动应用
    echo "=== 启动应用 ==="
    exec $VENV_PATH/bin/python src/web/app.py
else
    echo "=== 启动应用（系统 Python）==="
    exec python src/web/app.py
fi
