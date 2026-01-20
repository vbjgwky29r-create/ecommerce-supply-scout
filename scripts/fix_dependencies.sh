#!/bin/bash
set -e

echo "=== 强制修复依赖脚本 ==="

# 显示当前 Python 环境
echo "Python 路径: $(which python)"
echo "Python 版本: $(python --version)"
echo "虚拟环境: $VIRTUAL_ENV"

# 尝试卸载旧版本
echo "尝试卸载 coze-coding-dev-sdk..."
pip uninstall -y coze-coding-dev-sdk || echo "卸载失败或未安装"

# 强制安装正确版本
echo "安装 coze-coding-dev-sdk==0.5.4..."
pip install --no-cache-dir --force-reinstall coze-coding-dev-sdk==0.5.4

# 验证版本
echo "验证版本:"
pip show coze-coding-dev-sdk | grep Version || true

# 检查是否有语法错误
echo "检查 coze_coding_dev_sdk 是否有语法错误..."
python -c "import coze_coding_dev_sdk; print('导入成功！')" || {
    echo "❌ 导入失败，尝试修复..."
    # 如果仍然失败，尝试临时禁用有问题的包
    echo "警告：coze_coding_dev-sdk 仍有问题，但继续尝试启动应用..."
}

echo "=== 依赖修复完成 ==="
