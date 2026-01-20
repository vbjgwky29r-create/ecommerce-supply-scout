# 🚀 云端部署快速开始

## 📋 您的部署信息

- ✅ **GitHub 账号**：`vgjhwky29r-create`
- ✅ **GitHub 仓库**：`https://github.com/vbjgwky29r-create/ecommerce-supply-scout.git`
- ✅ **Railway 账号**：已就绪
- ✅ **API Key**：`e863036f-fe71-4771-9510-9a5d329d65c8`

---

## ⏱️ 5分钟完成云端部署

### 📤 步骤 1：上传代码到 GitHub（2分钟）

#### 方式 A：使用 GitHub Desktop（推荐新手）

1. 下载并安装：https://desktop.github.com/
2. 登录您的 GitHub 账号
3. 点击 "File" → "Add Local Repository"
4. 选择目录：`/workspace/projects`
5. 点击 "Publish repository"
6. 仓库名：`ecommerce-supply-scout`
7. 点击 "Publish"

#### 方式 B：使用 Git 命令行

```bash
cd /workspace/projects
git add .
git commit -m "feat: 初始版本"
git remote add origin https://github.com/vbjgwky29r-create/ecommerce-supply-scout.git
git branch -M main
git push -u origin main
```

**详细说明**：查看 [docs/upload-to-github.md](docs/upload-to-github.md)

---

### 🚂 步骤 2：在 Railway 部署（2分钟）

1. 访问：https://railway.app/
2. 点击 "Log in" → 使用 GitHub 登录
3. 点击 "New Project" → "Deploy from GitHub repo"
4. 搜索并选择：`ecommerce-supply-scout`
5. 点击 "Add Repo" → "Deploy Now"
6. 等待部署完成（约 2-3 分钟）

---

### ⚙️ 步骤 3：配置环境变量（1分钟）

在 Railway 项目页面，点击 "Variables" 标签，添加以下环境变量：

```
FLASK_SECRET_KEY=ecommerce-agent-secret-key-2024
COZE_WORKLOAD_IDENTITY_API_KEY=e863036f-fe71-4771-9510-9a5d329d65c8
```

**注意**：`DATABASE_URL` 会被 Railway 自动创建，无需手动添加。

配置完成后，点击 "Redeploy" 重新部署。

---

### 🌐 步骤 4：获取公网链接（30秒）

1. 部署成功后，在项目顶部看到访问地址，例如：
   ```
   https://ecommerce-scout.up.railway.app
   ```
2. 点击链接访问您的智能体
3. 将链接分享给朋友，在微信中即可使用

---

## 🎉 完成！

恭喜您！现在您的电商货源猎手智能体已经部署到云端，可以随时随地使用了。

### 📱 在微信中使用

1. 复制公网链接
2. 在微信中发送给朋友
3. 朋友点击链接即可使用

### 💬 使用示例

**寻找货源：**
```
帮我找一些适合在淘宝销售的冬季保暖用品货源
```

**分析图片：**
```
（上传一张商品图片）
帮我分析这款产品的市场潜力和竞争情况
```

**市场趋势：**
```
最近美妆行业有什么新的热门趋势？
```

---

## 📚 详细文档

- 📘 [完整部署指南](docs/deployment-guide.md)
- 📗 [代码上传指南](docs/upload-to-github.md)
- 📙 [项目 README](README.md)

---

## ❓ 遇到问题？

### 常见问题

**Q: 部署失败？**
A: 检查环境变量是否正确配置，特别是 API Key

**Q: 无法访问？**
A: 等待 2-3 分钟让应用完全启动，然后刷新页面

**Q: 图片上传失败？**
A: 确保图片小于 16MB，格式为 PNG/JPG/GIF/WEBP

**Q: 智能体无响应？**
A: 检查 API Key 是否有效，或等待几分钟后重试

### 技术支持

- 查看 Railway 日志：在项目页面点击 "Logs" 标签
- 检查浏览器控制台：按 F12 查看错误信息
- 查看完整文档：[docs/deployment-guide.md](docs/deployment-guide.md)

---

**祝您部署顺利，使用愉快！** 🚀
