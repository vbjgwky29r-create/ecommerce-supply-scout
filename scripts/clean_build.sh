#!/bin/bash
# 清理构建缓存和旧虚拟环境

echo "=== 清理构建缓存 ==="
rm -rf .venv
rm -rf build
rm -rf dist
rm -rf *.egg-info

echo "=== 安装依赖 ==="
pip install --no-cache-dir --upgrade pip
pip install --no-cache-dir -r requirements-render.txt

echo "=== 构建完成 ==="
