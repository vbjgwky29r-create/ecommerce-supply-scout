# 🚀 电商货源猎手智能体 - 云端部署指南

本指南将帮助您将电商货源猎手智能体部署到云端（Railway/Render），生成公网链接以便在微信中分享使用。

---

## 📋 前置准备

- ✅ GitHub 账号：`vgjhwky29r-create`
- ✅ Railway 账号（免费）
- ✅ API Key：`e863036f-fe71-4771-9510-9a5d329d65c8`
- ✅ 仓库地址：`https://github.com/vbjgwky29r-create/ecommerce-supply-scout.git`

---

## 📦 步骤 1：上传代码到 GitHub

由于云端部署需要从 GitHub 获取代码，我们首先需要将项目代码上传。

### 方法 1：使用 GitHub Desktop（推荐新手）

1. **下载 GitHub Desktop**
   - 访问：https://desktop.github.com/
   - 安装并登录您的 GitHub 账号

2. **添加本地仓库**
   - 点击 "File" → "Add Local Repository"
   - 选择项目目录：`/workspace/projects`

3. **发布到 GitHub**
   - 点击 "Publish repository"
   - 选择仓库：`ecommerce-supply-scout`
   - 勾选 "Keep this code private"（可选，建议选 Public）
   - 点击 "Publish repository"

### 方法 2：使用 Git 命令行

如果您熟悉 Git 命令行，可以使用以下命令：

```bash
# 1. 初始化 git 仓库（如果还没有）
cd /workspace/projects
git init

# 2. 添加所有文件
git add .

# 3. 创建首次提交
git commit -m "feat: 电商货源猎手智能体 - 初始版本"

# 4. 添加远程仓库
git remote add origin https://github.com/vbjgwky29r-create/ecommerce-supply-scout.git

# 5. 推送到 GitHub
git branch -M main
git push -u origin main
```

**⚠️ 注意**：推送时可能需要 GitHub 身份验证（Personal Access Token）。

---

## 🚂 步骤 2：在 Railway 部署

Railway 是一个现代化的云部署平台，支持从 GitHub 一键部署。

### 2.1 登录 Railway

1. 访问：https://railway.app/
2. 点击 "Log in"
3. 选择使用 GitHub 账号登录

### 2.2 创建新项目

1. 点击左侧的 "New Project" 按钮
2. 点击 "Deploy from GitHub repo"
3. 在搜索框中输入：`ecommerce-supply-scout`
4. 选择您的仓库
5. 点击 "Add Repo"

### 2.3 配置项目

1. **选择部署分支**：`main`
2. **设置项目名称**：`ecommerce-scout`（可自定义）
3. **选择环境变量**（下一步会详细配置）

4. 点击 "Deploy Now"

---

## ⚙️ 步骤 3：配置环境变量

在 Railway 项目中，我们需要配置以下环境变量：

### 必需的环境变量

1. **Flask 配置**
   - `FLASK_SECRET_KEY`：`ecommerce-agent-secret-key-2024`（或自定义密钥）

2. **大模型配置**
   - `COZE_WORKLOAD_IDENTITY_API_KEY`：`e863036f-fe71-4771-9510-9a5d329d65c8`

3. **数据库配置（Railway 会自动提供）**
   - `DATABASE_URL`：Railway 会自动创建 PostgreSQL 并提供此变量

### 配置步骤

1. **进入项目设置**
   - 在 Railway 项目页面，点击 "Variables" 标签

2. **添加环境变量**
   - 点击 "New Variable"
   - 依次添加上述环境变量

3. **重新部署**
   - 配置完成后，点击顶部 "Deployments" 标签
   - 点击最新部署记录旁的 "Redeploy" 按钮

---

## 🌐 步骤 4：获取公网访问链接

### 4.1 查看部署状态

1. 等待部署完成（通常需要 2-3 分钟）
2. 在 Railway 项目页面，您会看到绿色的 ✅ "Success" 状态

### 4.2 获取访问地址

1. 在项目顶部，您会看到一个 URL，例如：
   ```
   https://ecommerce-scout.up.railway.app
   ```

2. 点击该链接即可访问您的智能体

### 4.3 在微信中分享

1. 复制上述 URL
2. 在微信中发送给朋友
3. 朋友点击链接即可在微信浏览器中使用

---

## 🎨 使用说明

### 功能特性

- ✅ **文本对话**：与智能体进行自然语言交流
- ✅ **图片分析**：上传商品图片进行智能分析
- ✅ **货源搜索**：查找潜在热卖商品货源
- ✅ **市场趋势**：分析市场动态和趋势
- ✅ **产品评估**：评估产品潜力和竞争力

### 支持的图片格式

- PNG
- JPG / JPEG
- GIF
- WEBP

### 使用示例

**示例 1：寻找货源**
```
帮我找一些适合在淘宝销售的冬季保暖用品货源
```

**示例 2：分析产品**
```
我上传了一张连衣裙的图片，帮我分析这款产品的市场潜力和竞争情况
```

**示例 3：市场趋势**
```
最近美妆行业有什么新的热门趋势？
```

---

## 🔧 故障排除

### 问题 1：部署失败

**原因**：环境变量未正确配置

**解决方案**：
1. 检查所有必需的环境变量是否已添加
2. 确保 `COZE_WORKLOAD_IDENTITY_API_KEY` 格式正确
3. 点击 "Redeploy" 重新部署

### 问题 2：无法访问

**原因**：应用未完全启动

**解决方案**：
1. 等待 2-3 分钟，让应用完全启动
2. 检查 Railway 日志是否有错误
3. 尝试刷新页面

### 问题 3：图片上传失败

**原因**：文件过大或格式不支持

**解决方案**：
1. 确保图片小于 16MB
2. 使用支持的图片格式（PNG, JPG, GIF, WEBP）

### 问题 4：智能体无响应

**原因**：API Key 无效或限流

**解决方案**：
1. 检查 `COZE_WORKLOAD_IDENTITY_API_KEY` 是否正确
2. 确认 API Key 未过期
3. 如遇到限流，等待几分钟后重试

---

## 📊 Railway vs Render 对比

### Railway（推荐）

**优点：**
- ✅ 界面简洁，操作简单
- ✅ 免费额度：$5/月（512MB RAM, 0.5GB 硬盘）
- ✅ 自动生成 HTTPS
- ✅ 支持自定义域名
- ✅ 内置 PostgreSQL

**适用场景：**
- 新手快速部署
- 个人项目
- 需要数据库的应用

### Render

**优点：**
- ✅ 免费额度：750 小时/月（512MB RAM）
- ✅ 支持更多语言和框架
- ✅ 自动 HTTPS

**缺点：**
- ❌ 冷启动较慢（免费版）
- ❌ 免费版不支持 PostgreSQL

**适用场景：**
- 需要更多运行时间
- 不需要数据库的应用

---

## 💡 优化建议

### 1. 提升响应速度

- 启用缓存机制（已在代码中实现）
- 使用 CDN 加速静态资源
- 优化数据库查询

### 2. 节省配额

- 合理设置对话轮数限制（默认 20 轮）
- 使用缓存减少重复查询
- 定期清理过期数据

### 3. 扩展功能

- 添加用户认证系统
- 实现多用户会话管理
- 集成更多电商平台（京东、抖音等）

---

## 📞 技术支持

如遇到问题，请检查：

1. **Railway 日志**：查看部署和运行日志
2. **浏览器控制台**：检查前端错误
3. **网络连接**：确保可以访问公网

---

## 🎉 完成！

恭喜您完成云端部署！现在您可以将公网链接分享给朋友，在微信中愉快地使用电商货源猎手智能体了！

**示例分享文案：**
```
我找到了一个超好用的电商货源猎手智能体，可以帮我找热卖商品货源、分析市场趋势，还能识别商品图片！试试看：

https://ecommerce-scout.up.railway.app

#电商 #货源 #AI智能体
```

---

**祝您使用愉快！** 🚀
