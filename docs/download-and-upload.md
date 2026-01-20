# 📥 下载项目并上传到 GitHub

## 📦 步骤 1：下载项目压缩包

您的项目已打包为 `ecommerce-scout.tar.gz`（约 300KB）

### 下载方式

**如果您能访问服务器文件系统：**
1. 访问您的服务器/云环境文件管理器
2. 导航到：`/workspace/projects/`
3. 下载文件：`ecommerce-scout.tar.gz`

**如果您使用 SSH 访问：**
```bash
# 在本地电脑上执行
scp user@your-server:/workspace/projects/ecommerce-scout.tar.gz ~/Downloads/
```

**如果无法直接下载：**
请告诉我您使用的平台（如阿里云、腾讯云、AWS等），我会为您提供具体的下载方法。

---

## 🗂️ 步骤 2：解压文件

### Windows 用户

1. 下载并安装 7-Zip：https://www.7-zip.org/
2. 右键点击 `ecommerce-scout.tar.gz`
3. 选择 "7-Zip" → "提取到 ecommerce-scout\"

### Mac 用户

1. 双击 `ecommerce-scout.tar.gz` 即可自动解压

### Linux 用户

```bash
tar -xzf ecommerce-scout.tar.gz
cd ecommerce-scout
```

**解压后的目录结构：**
```
ecommerce-scout/
├── src/              # 源代码
│   ├── agents/       # Agent 代码
│   ├── tools/        # 工具
│   ├── web/          # Web 服务
│   └── storage/      # 存储层
├── config/           # 配置文件
├── docs/             # 文档
├── scripts/          # 脚本
├── assets/           # 资源
├── requirements.txt  # Python 依赖
├── Procfile          # 部署配置
├── railway.toml      # Railway 配置
├── README.md         # 项目说明
└── QUICKSTART.md     # 快速开始指南
```

---

## 🖥️ 步骤 3：安装 GitHub Desktop

### 下载 GitHub Desktop

访问：https://desktop.github.com/

选择适合您操作系统的版本：
- **Windows**：点击 "Download for Windows"
- **macOS**：点击 "Download for macOS"

### 安装并登录

1. **安装软件**
   - Windows：双击下载的 `.exe` 文件，按提示安装
   - macOS：双击下载的 `.dmg` 文件，拖拽到 Applications 文件夹

2. **登录 GitHub**
   - 打开 GitHub Desktop
   - 点击 "File" → "Options" (Windows) 或 "Preferences" (Mac)
   - 点击 "Accounts"
   - 点击 "Sign in with your browser"
   - 在浏览器中登录您的 GitHub 账号（vgjhwky29r-create）
   - 返回 GitHub Desktop，确认登录成功

---

## 📤 步骤 4：将项目发布到 GitHub

### 4.1 添加本地仓库

1. 打开 GitHub Desktop
2. 点击左上角的 "File" 菜单
3. 选择 "Add Local Repository..."
4. 浏览到您解压的项目目录
   - 例如：`C:\Users\YourName\Downloads\ecommerce-scout`
   - 或：`/Users/YourName/Downloads/ecommerce-scout`
5. 点击 "Add repository"

### 4.2 发布到 GitHub

1. 在 GitHub Desktop 界面中，您会看到项目文件
2. 点击顶部的 "Publish repository" 按钮
3. 填写仓库信息：
   - **Name**: `ecommerce-supply-scout`
   - **Description**: 电商货源猎手智能体 - 帮助卖家高效寻找热卖商品货源
   - **Visibility**: 选择 "Public"（公开，可免费分享）
4. 点击 "Publish repository"

### 4.3 验证上传成功

1. 访问：https://github.com/vbjgwky29r-create/ecommerce-supply-scout
2. 确认看到以下文件：
   - ✅ `src/agents/agent.py`
   - ✅ `src/web/app.py`
   - ✅ `src/web/templates/index.html`
   - ✅ `config/agent_llm_config.json`
   - ✅ `requirements.txt`
   - ✅ `Procfile`
   - ✅ `railway.toml`
   - ✅ `README.md`
   - ✅ `QUICKSTART.md`

---

## 🚀 步骤 5：在 Railway 部署

### 5.1 登录 Railway

1. 访问：https://railway.app/
2. 点击 "Log in"
3. 选择使用 GitHub 账号登录

### 5.2 创建新项目

1. 点击左侧的 "New Project" 按钮
2. 点击 "Deploy from GitHub repo"
3. 在搜索框中输入：`ecommerce-supply-scout`
4. 选择您的仓库（vgjhwky29r-create/ecommerce-supply-scout）
5. 点击 "Add Repo"

### 5.3 配置部署

1. **选择分支**：`main`
2. **项目名称**：`ecommerce-scout`（可自定义）
3. **点击 "Deploy Now"**

### 5.4 等待部署完成

- 部署过程大约需要 2-3 分钟
- 您可以在 "Deployments" 页面看到实时进度
- 成功后会显示 ✅ "Success" 状态

---

## ⚙️ 步骤 6：配置环境变量

### 6.1 打开变量设置

1. 在 Railway 项目页面
2. 点击顶部的 "Variables" 标签

### 6.2 添加必需的环境变量

点击 "New Variable"，依次添加以下变量：

**1. Flask 配置**
```
FLASK_SECRET_KEY=ecommerce-agent-secret-key-2024
```

**2. 大模型 API Key**
```
COZE_WORKLOAD_IDENTITY_API_KEY=e863036f-fe71-4771-9510-9a5d329d65c8
```

**3. 数据库配置（Railway 自动创建）**
```
DATABASE_URL=（Railway 会自动生成，无需手动添加）
```

### 6.3 重新部署

1. 配置完成后，点击 "Deployments" 标签
2. 点击最新部署记录旁的 "Redeploy" 按钮
3. 等待重新部署完成（约 1-2 分钟）

---

## 🌐 步骤 7：获取公网访问链接

### 7.1 查看应用地址

1. 部署成功后，在项目顶部会显示应用 URL
2. 例如：`https://ecommerce-scout.up.railway.app`
3. 点击链接即可访问您的智能体

### 7.2 分享给朋友

1. 复制应用 URL
2. 在微信中发送给朋友
3. 朋友点击链接即可在微信浏览器中使用

### 分享文案示例

```
我找到了一个超好用的电商货源猎手智能体！

✅ 可以搜索热卖商品货源
✅ 分析市场趋势和竞争情况
✅ 上传图片自动识别产品
✅ 计算利润和投资回报率

试试看：https://ecommerce-scout.up.railway.app

#电商 #货源 #AI智能体
```

---

## 🎉 完成！

恭喜您完成云端部署！现在您可以：

✅ 随时随地通过公网链接访问智能体
✅ 在微信中分享给朋友使用
✅ 享受 Railway 免费额度（$5/月）

---

## 📚 相关文档

- 📘 [快速开始指南](../QUICKSTART.md)
- 📗 [完整部署教程](deployment-guide.md)
- 📙 [项目 README](../README.md)

---

## ❓ 遇到问题？

### 常见问题及解决方法

**Q1: 下载压缩包失败？**
A: 请告诉我您使用的云平台，我会提供具体的下载方法。

**Q2: GitHub Desktop 无法安装？**
A: 检查系统要求，确保操作系统版本兼容。

**Q3: GitHub Desktop 无法登录？**
A: 检查网络连接，确保可以访问 GitHub。

**Q4: 上传速度慢？**
A: 压缩包只有 300KB，应该很快。如果仍然慢，请检查网络连接。

**Q5: Railway 部署失败？**
A: 检查环境变量是否正确配置，查看 Railway 日志了解错误详情。

**Q6: 无法访问应用？**
A: 等待 2-3 分钟让应用完全启动，然后刷新页面。

---

## 💡 提示

1. ** Railway 免费额度**：每月 $5，足够个人项目使用
2. **自动休眠**：30分钟无访问会自动休眠，重新访问需要 30秒 冷启动
3. **数据保留**：所有数据保存在 Railway 的 PostgreSQL 数据库中，不会丢失
4. **自定义域名**：可以在 Railway 设置中绑定自定义域名（需要拥有域名）

---

**祝您部署顺利，使用愉快！** 🚀
