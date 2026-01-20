# 🚀 在 Render 上部署电商货源猎手（免费，可分享给朋友）

Render 是另一个优秀的云平台，支持 Python 应用，提供免费额度，部署也非常简单！

## 📋 部署前准备

1. **注册 Render 账号**
   - 访问：https://render.com/
   - 点击 "Sign Up"
   - 使用 GitHub 账号登录（推荐）

2. **准备代码**
   - 确保项目根目录下有以下文件：
     - `Procfile`
     - `requirements-railway.txt`
     - `src/web/app.py`
     - `src/agents/agent.py`

## 🚀 部署步骤

### 步骤1: 推送代码到 GitHub

```bash
# 初始化 git 仓库（如果还没有）
git init

# 添加所有文件
git add .

# 提交
git commit -m "部署到Render"

# 创建 GitHub 仓库并推送
git remote add origin https://github.com/你的用户名/你的仓库名.git
git branch -M main
git push -u origin main
```

### 步骤2: 在 Render 上创建 Web Service

1. 登录 Render: https://dashboard.render.com/
2. 点击 "New +"
3. 选择 "Web Service"
4. 选择 "Build and deploy from a Git repository"
5. 选择你的 GitHub 仓库
6. 配置构建选项：

**配置详情**:

```
Name: ecommerce-agent
Environment: Python 3
Region: Singapore（或其他离你最近的区域）
Branch: main
Root Directory: ./
Build Command: pip install -r requirements-railway.txt
Start Command: python src/web/app.py
```

7. 点击 "Create Web Service"

### 步骤3: 配置环境变量

在 Web Service 页面，点击 "Environment" 添加以下变量：

```bash
# API Key（必需）
COZE_WORKLOAD_IDENTITY_API_KEY=你的API密钥

# 模型服务地址（必需）
COZE_INTEGRATION_MODEL_BASE_URL=https://ark.cn-beijing.volces.com/api/v3

# Flask配置
FLASK_SECRET_KEY=随机生成的密钥
WEB_HOST=0.0.0.0
WEB_PORT=5000

# 数据库配置（如果需要）
DATABASE_URL=postgresql://user:password@host:port/database
```

### 步骤4: 添加数据库（可选）

如果需要使用数据库：

1. 在 Render 点击 "New +"
2. 选择 "PostgreSQL"
3. 创建数据库
4. 在 Web Service 页面，复制 `DATABASE_URL` 到环境变量中

### 步骤5: 获取访问链接

部署成功后，Render 会自动生成一个类似这样的链接：

```
https://ecommerce-agent.onrender.com
```

**这就是你的公网链接！可以分享给任何人使用！** 🎉

### 步骤6: 配置自定义域名（可选）

1. 在 Web Service 页面，点击 "Custom Domains"
2. 添加你的域名
3. 按照提示配置 DNS

## 💰 费用说明

Render 免费计划包含：

- **Web Service**: 750 小时/月（约31天）
- **数据库**: 90天免费试用
- **存储**: 100 MB

对于个人使用，完全免费！

如果需要更多资源：
- Starter Plan: $7/月

## 📱 如何分享给朋友

与 Railway 相同，直接分享链接即可！

```
https://你的应用名.onrender.com
```

## 🔧 常见问题

### Q: 部署后一直显示 "Deploying"？

**A**:
1. 查看部署日志
2. 检查构建命令是否正确
3. 确保依赖都能成功安装

### Q: 服务启动失败？

**A**:
1. 检查 Start Command 是否正确
2. 确保端口绑定到 0.0.0.0
3. 查看日志排查错误

### Q: 服务自动休眠怎么办？

**A**: Render 免费计划会在 15 分钟无访问后自动休眠，这是正常的。
- 有访问时会自动唤醒
- 首次访问可能需要 30-60 秒启动时间
- 可以通过定期 ping 保持唤醒

### Q: 如何查看日志？

**A**:
1. 在 Web Service 页面点击 "Logs"
2. 可以查看实时日志
3. 也可以下载历史日志

## 🚀 进阶配置

### 1. 配置自动休眠策略

在 `render.yaml` 中配置：

```yaml
services:
  - type: web
    name: ecommerce-agent
    env: python
    # 其他配置...
```

### 2. 配置健康检查

Render 会自动检测 `/health` 端点。

### 3. 配置自动部署

连接 GitHub 仓库后，每次推送代码会自动重新部署。

## 📚 相关资源

- Render 官网: https://render.com/
- Render 文档: https://render.com/docs/
- Python 部署指南: https://render.com/docs/deploy-python-example

## 🎉 完成！

现在你的电商货源猎手已经部署到 Render，可以分享给任何人使用了！

**分享链接示例**:
```
https://你的应用名.onrender.com
```

## 🔄 Railway vs Render 对比

| 特性 | Railway | Render |
|------|---------|--------|
| 免费额度 | $5/月 | 750小时/月 |
| 部署速度 | 快 | 较慢 |
| 数据库 | 免费支持 | 90天试用 |
| 自定义域名 | 支持 | 支持 |
| 自动休眠 | 无 | 15分钟后休眠 |
| 推荐指数 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

**我的建议**: 如果需要长期稳定运行，推荐 **Railway**；如果只是偶尔使用，**Render** 也可以。

## 💡 快速选择

- **推荐 Railway**: 想要稳定、长期使用
- **可选 Render**: 想要尝试不同的平台

现在选择一个平台开始部署吧！🚀
