# 📤 将项目上传到 GitHub - 完整指南

## 🎯 目标

将电商货源猎手项目上传到 GitHub，然后可以部署到 Railway/Render 等平台。

## 📋 步骤1: 在 GitHub 上创建仓库

### 1.1 访问 GitHub

打开浏览器，访问：https://github.com/

### 1.2 登录/注册账号

如果还没有账号，先注册一个（免费）。

### 1.3 创建新仓库

1. 点击右上角的 **+** 号
2. 选择 **New repository**
3. 填写仓库信息：
   - **Repository name**: `ecommerce-sourcing-agent`（或其他你喜欢的名字）
   - **Description**: `电商货源猎手智能体 - 帮助卖家寻找热卖货源`
   - **Public**: 选择 `Public`（公开）
   - **Private**: 选择 `Private`（私有）
4. **⚠️ 不要勾选**:
   - [ ] Add a README file
   - [ ] Add .gitignore
   - [ ] Choose a license
5. 点击 **Create repository**

### 1.4 保存仓库地址

创建成功后，GitHub 会显示仓库地址，类似：
```
https://github.com/你的用户名/ecommerce-sourcing-agent.git
```

**复制这个地址，后面会用到！**

---

## 📋 步骤2: 连接本地项目到 GitHub

### 2.1 检查当前项目状态

```bash
cd /workspace/projects
git status
```

### 2.2 添加远程仓库

将 GitHub 仓库添加为远程仓库（替换 `你的用户名`）：

```bash
git remote add origin https://github.com/你的用户名/ecommerce-sourcing-agent.git
```

### 2.3 验证远程仓库

```bash
git remote -v
```

应该看到类似输出：
```
origin  https://github.com/你的用户名/ecommerce-sourcing-agent.git (fetch)
origin  https://github.com/你的用户名/ecommerce-sourcing-agent.git (push)
```

---

## 📋 步骤3: 推送代码到 GitHub

### 3.1 查看当前分支

```bash
git branch
```

### 3.2 推送到 GitHub

```bash
git push -u origin main
```

**如果提示需要登录**:
1. 会弹出 GitHub 登录页面
2. 输入你的 GitHub 账号密码
3. 或使用 Personal Access Token（推荐）

**如何创建 Personal Access Token**:
1. 访问：https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 勾选 `repo` 权限
4. 点击 "Generate token"
5. 复制 token（只显示一次！）
6. 使用 token 代替密码登录

---

## 📋 步骤4: 验证上传成功

### 4.1 在 GitHub 上查看

1. 访问你的仓库地址：`https://github.com/你的用户名/ecommerce-sourcing-agent`
2. 查看文件是否都已上传
3. 确认重要文件都在：
   - ✅ `Procfile`
   - ✅ `railway.toml`
   - ✅ `requirements-railway.txt`
   - ✅ `src/web/app.py`
   - ✅ `src/agents/agent.py`

### 4.2 检查文件列表

GitHub 仓库应该包含以下文件和文件夹：
```
ecommerce-sourcing-agent/
├── Procfile
├── railway.toml
├── requirements-railway.txt
├── requirements.txt
├── AGENT.md
├── README.md
├── .gitignore
├── src/
│   ├── agents/
│   │   └── agent.py
│   ├── web/
│   │   ├── app.py
│   │   └── templates/
│   │       └── index.html
│   ├── storage/
│   │   ├── database/
│   │   │   └── ...
│   │   └── memory/
│   │       └── ...
│   ├── tools/
│   ├── utils/
│   └── main.py
├── config/
│   └── agent_llm_config.json
├── scripts/
│   └── start_web.sh
├── docs/
│   ├── DEPLOYMENT_QUICKSTART.md
│   ├── DEPLOY_TO_RAILWAY.md
│   ├── DEPLOY_TO_RENDER.md
│   └── ...
└── tests/
```

---

## 📋 步骤5: 配置 GitHub 仓库（重要）

### 5.1 设置仓库描述

1. 在 GitHub 仓库页面，点击右上角 ⚙️ 设置图标
2. 在 "Description" 中填写：`电商货源猎手智能体 - 帮助卖家寻找热卖货源`
3. 点击 "Save"

### 5.2 设置可见性

1. 在设置页面，找到 "Danger Zone"
2. 如果要公开，点击 "Change visibility" → "Make public"
3. 如果要私有，点击 "Change visibility" → "Make private"
4. **部署到 Railway/Render 需要公开仓库**

### 5.3 添加 Topics（标签）

1. 在仓库主页面，找到 "Topics"
2. 添加以下标签：
   - `ecommerce`
   - `ai`
   - `agent`
   - `langchain`
   - `web-app`
   - `flask`

---

## 🚀 步骤6: 部署到 Railway（可选）

### 6.1 访问 Railway

打开：https://railway.app/

### 6.2 登录

点击 "Log in"，使用 GitHub 账号登录。

### 6.3 创建项目

1. 点击 "New Project"
2. 选择 "Deploy from GitHub repo"
3. 找到你刚上传的仓库
4. 点击 "Deploy"

### 6.4 配置环境变量

Railway 会自动检测 Python 项目，你需要添加环境变量：

1. 在项目页面，点击 "Variables"
2. 添加以下变量：

```bash
COZE_WORKLOAD_IDENTITY_API_KEY=你的API密钥
COZE_INTEGRATION_MODEL_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
FLASK_SECRET_KEY=随机生成的密钥
```

### 6.5 等待部署

Railway 会自动构建和部署，约3-5分钟完成。

### 6.6 获取访问链接

部署成功后，你会得到一个链接：
```
https://你的应用名-production.up.railway.app
```

**这就是可以分享给朋友的链接！**

---

## ❓ 常见问题

### Q: 提示 "Permission denied" 怎么办？

**A**: 使用 Personal Access Token 代替密码：
1. 访问：https://github.com/settings/tokens
2. 创建新 token，勾选 `repo` 权限
3. 复制 token
4. 在推送时使用 token 作为密码

### Q: 推送很慢或失败？

**A**: 可能是网络问题，尝试：
1. 使用 GitHub Desktop（图形界面）
2. 使用代理
3. 多尝试几次

### Q: 忘记添加 `.gitignore` 怎么办？

**A**: 已经添加了！如果需要修改：
1. 编辑 `.gitignore` 文件
2. 运行：
   ```bash
   git add .gitignore
   git commit -m "Update .gitignore"
   git push
   ```

### Q: 如何删除文件？

**A**:
```bash
git rm 文件名
git commit -m "Delete file"
git push
```

### Q: 如何创建分支？

**A**:
```bash
git checkout -b feature/新功能
# 做一些修改
git add .
git commit -m "Add new feature"
git push origin feature/新功能
```

---

## 🎉 完成！

现在你的项目已经在 GitHub 上了！可以：
1. ✅ 部署到 Railway
2. ✅ 部署到 Render
3. ✅ 与他人协作
4. ✅ 备份代码

**下一步**: 查看 [docs/DEPLOYMENT_QUICKSTART.md](./DEPLOYMENT_QUICKSTART.md) 开始部署到云端！

---

## 💡 实用命令

### 查看远程仓库
```bash
git remote -v
```

### 查看提交历史
```bash
git log --oneline
```

### 查看文件修改
```bash
git diff
```

### 撤销未提交的修改
```bash
git checkout -- 文件名
```

### 拉取最新代码
```bash
git pull origin main
```

---

## 📚 相关资源

- GitHub 官方文档: https://docs.github.com/
- Git 教程: https://www.runoob.com/git/git-tutorial.html
- GitHub 新手指南: https://github.com/

---

## 🚀 开始上传吧！

按照上面的步骤，5分钟就能把项目上传到 GitHub！

**准备好了吗？开始吧！** 🎉
