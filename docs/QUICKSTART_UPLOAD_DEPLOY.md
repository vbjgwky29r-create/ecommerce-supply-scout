# 🚀 快速开始：上传到 GitHub 并部署

## 📋 5分钟快速流程

### 第一步：在 GitHub 创建仓库（2分钟）

1. 访问：https://github.com/new
2. 填写信息：
   - **Repository name**: `ecommerce-sourcing-agent`
   - **Public**: 选择公开（部署需要）
   - ⚠️ 不要勾选任何选项（README、.gitignore、License）
3. 点击 **Create repository**
4. **复制仓库地址**，例如：
   ```
   https://github.com/你的用户名/ecommerce-sourcing-agent.git
   ```

---

### 第二步：使用脚本上传（2分钟）

在项目根目录运行：

```bash
./scripts/upload_to_github.sh
```

按照提示操作：
1. 输入你的 GitHub 仓库地址
2. 确认推送
3. 输入 GitHub 用户名和密码（或使用 Personal Access Token）

**完成！** 项目已上传到 GitHub。

---

### 第三步：部署到 Railway（1分钟）

1. 访问：https://railway.app/
2. 点击 "Log in"（使用 GitHub 登录）
3. 点击 "New Project"
4. 选择 "Deploy from GitHub repo"
5. 找到并选择你的仓库
6. 点击 "Deploy"
7. 等待3-5分钟
8. 在 "Variables" 添加环境变量：
   ```
   COZE_WORKLOAD_IDENTITY_API_KEY=你的API密钥
   COZE_INTEGRATION_MODEL_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
   FLASK_SECRET_KEY=随机密钥
   ```

**完成！** 获得访问链接，可以分享给朋友了！

---

## 🎯 完整详细教程

### 📖 上传到 GitHub

查看详细教程：[docs/UPLOAD_TO_GITHUB.md](./UPLOAD_TO_GITHUB.md)

包含：
- 图文步骤
- 常见问题解决
- 实用命令

### 📖 部署到 Railway

查看详细教程：[docs/DEPLOY_TO_RAILWAY.md](./DEPLOY_TO_RAILWAY.md)

包含：
- 环境变量配置
- 数据库设置
- 自定义域名
- 故障排查

### 📖 部署到 Render

查看详细教程：[docs/DEPLOY_TO_RENDER.md](./DEPLOY_TO_RENDER.md)

完全免费，适合小范围分享。

---

## 💡 获取 API Key

部署时需要以下环境变量：

```
COZE_WORKLOAD_IDENTITY_API_KEY=你的API密钥
COZE_INTEGRATION_MODEL_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
FLASK_SECRET_KEY=随机密钥
```

**如何获取 API Key**:
1. 访问火山引擎方舟：https://console.volcengine.com/ark
2. 登录后进入 API Key 管理
3. 创建新的 API Key
4. 复制并保存

**如何生成随机密钥**:
```bash
# Linux/Mac
openssl rand -hex 32

# 在线生成
# 访问 https://www.random.org/strings/
```

---

## ✅ 验证部署成功

### 检查 GitHub 仓库

访问你的仓库，确认文件都已上传：
- ✅ `Procfile`
- ✅ `railway.toml`
- ✅ `requirements-railway.txt`
- ✅ `src/web/app.py`
- ✅ `src/agents/agent.py`

### 检查 Railway 部署

访问 Railway 项目页面，确认：
- ✅ 状态显示 "Running"
- ✅ 点击生成的链接能访问
- ✅ 可以正常使用

### 测试功能

在浏览器或微信中打开链接：
1. 测试文本对话
2. 测试图片上传
3. 测试流式响应

---

## 🎉 分享给朋友

### 分享链接

Railway 会生成类似这样的链接：
```
https://ecommerce-agent-production.up.railway.app
```

### 分享方式

1. **直接分享链接**
   - 微信、QQ、邮件

2. **生成二维码**
   - 访问：https://www.qrcode-generator.com/
   - 输入链接生成二维码

3. **创建短链接**
   - 使用短链接服务（如 dwz.cn）

---

## 🆘 常见问题

### Q: 脚本运行失败？

**A**: 检查：
1. 是否在项目根目录
2. 是否有 git 命令
3. 网络是否正常

### Q: 推送到 GitHub 失败？

**A**:
1. 检查仓库地址是否正确
2. 使用 Personal Access Token 代替密码
3. 确保有推送权限

### Q: Railway 部署失败？

**A**:
1. 检查环境变量是否配置
2. 查看部署日志
3. 确认 API Key 是否有效

### Q: 链接打不开？

**A**:
1. 检查 Railway 服务是否运行
2. 查看健康检查状态
3. 尝试刷新页面

---

## 📚 相关文档

- **上传到 GitHub**: [docs/UPLOAD_TO_GITHUB.md](./UPLOAD_TO_GITHUB.md)
- **部署快速开始**: [docs/DEPLOYMENT_QUICKSTART.md](./DEPLOYMENT_QUICKSTART.md)
- **Railway 部署**: [docs/DEPLOY_TO_RAILWAY.md](./DEPLOY_TO_RAILWAY.md)
- **Render 部署**: [docs/DEPLOY_TO_RENDER.md](./DEPLOY_TO_RENDER.md)
- **方案对比**: [docs/DEPLOYMENT_COMPARISON.md](./DEPLOYMENT_COMPARISON.md)

---

## 🚀 立即开始！

### 选择你的路径：

**路径1：完全新手**
1. 阅读 [docs/UPLOAD_TO_GITHUB.md](./UPLOAD_TO_GITHUB.md)
2. 按步骤操作上传
3. 阅读 [docs/DEPLOY_TO_RAILWAY.md](./DEPLOY_TO_RAILWAY.md)
4. 按步骤部署

**路径2：快速开始**
1. 在 GitHub 创建仓库
2. 运行 `./scripts/upload_to_github.sh`
3. 在 Railway 部署
4. 完成！

**路径3：熟练用户**
1. Git push 到 GitHub
2. Railway 部署
3. 配置环境变量
4. 分享链接

---

## 🎉 10分钟后

你就能把链接分享给朋友了！

**分享链接示例**:
```
https://ecommerce-agent-production.up.railway.app
```

朋友点击链接，就能在微信中使用你的智能体！

**开始吧！** 🚀
