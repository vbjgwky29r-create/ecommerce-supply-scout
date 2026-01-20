# 📤 代码上传指南

由于云端环境的限制，请选择以下任一方式将代码上传到 GitHub。

---

## 🎯 方案 1：使用 GitHub Desktop（推荐，最简单）

### 步骤 1：下载并安装 GitHub Desktop

访问：https://desktop.github.com/
下载并安装适合您系统的版本。

### 步骤 2：登录 GitHub 账号

1. 打开 GitHub Desktop
2. 点击 "File" → "Options" (Windows) 或 "Preferences" (Mac)
3. 点击 "Accounts"
4. 点击 "Sign in" 并选择 "Sign in with your browser"
5. 登录您的 GitHub 账号（vgjhwky29r-create）

### 步骤 3：添加本地仓库

1. 点击 "File" → "Add Local Repository"
2. 浏览到项目目录：`/workspace/projects`
3. 选择文件夹并点击 "Add repository"

### 步骤 4：发布到 GitHub

1. 在 GitHub Desktop 界面，点击 "Publish repository" 按钮
2. 填写仓库信息：
   - **Name**: `ecommerce-supply-scout`
   - **Description**: 电商货源猎手智能体 - 帮助卖家高效寻找热卖商品货源
   - **Visibility**: 选择 "Public"（公开，可免费分享）
3. 点击 "Publish repository"

完成！代码已成功上传到 GitHub。

---

## 🎯 方案 2：使用 Git 命令行（需要 Personal Access Token）

### 步骤 1：创建 GitHub Personal Access Token

1. 访问：https://github.com/settings/tokens
2. 点击 "Generate new token" → "Generate new token (classic)"
3. 配置 Token：
   - **Note**: `ecommerce-scout-deployment`
   - **Expiration**: 选择 `90 days` 或 `No expiration`
   - **Scopes**: 勾选 `repo` (完整的仓库访问权限)
4. 点击 "Generate token"
5. **重要**：复制生成的 Token（格式：`ghp_xxxxxxxxxxxxxxxxxxxx`）

### 步骤 2：在项目中执行 Git 命令

打开终端，进入项目目录：

```bash
cd /workspace/projects
```

执行以下命令：

```bash
# 1. 检查 git 状态
git status

# 2. 添加所有文件
git add .

# 3. 创建提交
git commit -m "feat: 电商货源猎手智能体 - 初始版本

- 实现联网搜索和市场趋势分析
- 集成 PostgreSQL 数据库存储
- 支持多模态图片分析
- 提供 Flask Web 服务和 WebSocket 支持
- 完整的云端部署配置"

# 4. 添加远程仓库
git remote add origin https://github.com/vbjgwky29r-create/ecommerce-supply-scout.git

# 5. 推送到 GitHub（会提示输入用户名和密码）
git branch -M main
git push -u origin main
```

### 步骤 3：身份验证

当执行 `git push` 时，系统会提示：

```
Username: vgjhwky29r-create
Password: [粘贴您的 Personal Access Token]
```

**⚠️ 注意**：密码处粘贴刚才生成的 Token，而不是 GitHub 账号密码！

---

## 🎯 方案 3：使用在线工具（无需本地安装）

如果您不方便安装软件，可以使用以下在线方式：

### 步骤 1：创建项目压缩包

```bash
cd /workspace/projects
tar -czf ecommerce-scout.tar.gz \
  src/ \
  config/ \
  docs/ \
  scripts/ \
  requirements.txt \
  Procfile \
  railway.toml \
  README.md \
  AGENT.md
```

### 步骤 2：下载压缩包

将 `ecommerce-scout.tar.gz` 下载到您的本地电脑。

### 步骤 3：使用 GitHub 网页界面

1. 访问：https://github.com/vbjgwky29r-create/ecommerce-supply-scout
2. 点击 "Add file" → "Upload files"
3. 解压压缩包，将所有文件拖拽到上传区域
4. 填写提交信息：
   ```
   feat: 电商货源猎手智能体 - 初始版本
   ```
5. 点击 "Commit changes"

---

## ✅ 验证上传成功

无论使用哪种方案，上传成功后，您应该能在以下地址看到所有文件：

**仓库地址**：https://github.com/vbjgwky29r-create/ecommerce-supply-scout

检查以下文件是否存在：

- ✅ `src/agents/agent.py`
- ✅ `src/tools/`
- ✅ `src/web/app.py`
- ✅ `src/web/templates/index.html`
- ✅ `config/agent_llm_config.json`
- ✅ `requirements.txt`
- ✅ `Procfile`
- ✅ `railway.toml`

---

## 🚀 上传成功后下一步

确认代码上传成功后，请返回主部署指南：

**查看部署指南**：[docs/deployment-guide.md](deployment-guide.md)

继续执行 **步骤 2：在 Railway 部署**。

---

## 📞 常见问题

### Q1: 推送时出现 "Authentication failed" 错误

**A**: 检查以下几点：
1. Personal Access Token 是否已复制完整
2. Token 是否勾选了 `repo` 权限
3. 用户名是否正确（vgjhwky29r-create）

### Q2: GitHub Desktop 无法找到项目目录

**A**: 确保您选择的是 `/workspace/projects` 目录，该目录应该包含 `.git` 文件夹。

### Q3: 网页上传速度慢

**A**: 文件较多时，网页上传可能较慢。建议使用方案 1（GitHub Desktop）或方案 2（Git 命令行）。

---

## 💡 提示

**推荐顺序**：方案 1 → 方案 2 → 方案 3

方案 1（GitHub Desktop）最简单，适合新手。
方案 2（Git 命令行）最灵活，适合有经验的开发者。
方案 3（网页上传）最慢，仅适用于文件较少的情况。

---

**祝您上传顺利！** 🎉
