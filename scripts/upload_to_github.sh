#!/bin/bash

# 上传项目到 GitHub 的辅助脚本

echo "=========================================="
echo "  上传项目到 GitHub"
echo "=========================================="
echo ""

# 检查是否在项目根目录
if [ ! -f "requirements.txt" ]; then
    echo "错误: 请在项目根目录下运行此脚本"
    exit 1
fi

# 设置工作目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

echo "📂 工作目录: $PROJECT_DIR"
echo ""

# 检查 Git 仓库
if [ ! -d ".git" ]; then
    echo "初始化 Git 仓库..."
    git init
    echo "✅ Git 仓库初始化完成"
else
    echo "✅ Git 仓库已存在"
fi

echo ""

# 检查远程仓库
if [ -z "$(git remote -v)" ]; then
    echo "⚠️  尚未配置远程仓库"
    echo ""
    echo "请按照以下步骤操作："
    echo "1. 访问 https://github.com/new"
    echo "2. 创建新仓库"
    echo "3. 复制仓库地址（如：https://github.com/你的用户名/你的仓库名.git）"
    echo ""
    read -p "请输入你的 GitHub 仓库地址: " REPO_URL

    if [ -z "$REPO_URL" ]; then
        echo "❌ 仓库地址不能为空"
        exit 1
    fi

    git remote add origin "$REPO_URL"
    echo "✅ 远程仓库已添加: $REPO_URL"
else
    echo "✅ 远程仓库已配置:"
    git remote -v
fi

echo ""

# 检查是否有未提交的更改
if [ -n "$(git status --porcelain)" ]; then
    echo "📝 检测到未提交的更改，正在提交..."
    git add .
    git commit -m "Update project files"
    echo "✅ 更改已提交"
else
    echo "✅ 没有未提交的更改"
fi

echo ""
echo "=========================================="
echo "  准备推送到 GitHub"
echo "=========================================="
echo ""
echo "当前分支: $(git branch --show-current)"
echo "远程仓库: $(git remote get-url origin)"
echo ""

# 确认推送
read -p "是否现在推送到 GitHub? (y/n): " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 已取消推送"
    echo ""
    echo "💡 提示: 以后可以手动运行以下命令推送:"
    echo "   git push -u origin main"
    exit 0
fi

echo ""
echo "🚀 开始推送..."
echo ""

# 推送到 GitHub
if git push -u origin main; then
    echo ""
    echo "=========================================="
    echo "  ✅ 推送成功！"
    echo "=========================================="
    echo ""
    echo "📦 仓库地址: $(git remote get-url origin)"
    echo ""
    echo "下一步:"
    echo "1. 在浏览器中打开你的 GitHub 仓库"
    echo "2. 验证文件是否都已上传"
    echo "3. 开始部署到 Railway 或 Render"
    echo ""
    echo "📚 查看部署文档:"
    echo "   - 快速开始: docs/DEPLOYMENT_QUICKSTART.md"
    echo "   - Railway: docs/DEPLOY_TO_RAILWAY.md"
    echo "   - Render: docs/DEPLOY_TO_RENDER.md"
    echo ""
else
    echo ""
    echo "=========================================="
    echo "  ❌ 推送失败"
    echo "=========================================="
    echo ""
    echo "可能的原因:"
    echo "1. 用户名或密码错误"
    echo "2. 网络问题"
    echo "3. 权限不足"
    echo ""
    echo "💡 解决方案:"
    echo "1. 使用 Personal Access Token 代替密码"
    echo "   访问: https://github.com/settings/tokens"
    echo "   创建 token，勾选 'repo' 权限"
    echo ""
    echo "2. 手动推送:"
    echo "   git push -u origin main"
    echo ""
    exit 1
fi
