# 🚀 在 Railway 上部署电商货源猎手（免费，可分享给朋友）

Railway 是一个现代化的云平台，支持 Python 应用，部署超级简单，有免费额度！

## 📋 部署前准备

1. **注册 Railway 账号**
   - 访问：https://railway.app/
   - 点击 "Start a new project"
   - 使用 GitHub 账号登录（推荐）或邮箱注册

2. **准备代码**
   - 确保项目根目录下有以下文件：
     - `Procfile`
     - `railway.toml`
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
git commit -m "部署到Railway"

# 创建 GitHub 仓库并推送
# 1. 在 GitHub 上创建新仓库
# 2. 然后执行：
git remote add origin https://github.com/你的用户名/你的仓库名.git
git branch -M main
git push -u origin main
```

### 步骤2: 在 Railway 上创建项目

1. 登录 Railway: https://railway.app/
2. 点击 "New Project"
3. 选择 "Deploy from GitHub repo"
4. 选择你的仓库
5. Railway 会自动检测 Python 项目并开始部署

### 步骤3: 配置环境变量

部署后，需要添加必要的环境变量：

1. 在 Railway 项目页面，点击 "Variables"
2. 添加以下环境变量：

```bash
# API Key（必需）
COZE_WORKLOAD_IDENTITY_API_KEY=你的API密钥

# 模型服务地址（必需）
COZE_INTEGRATION_MODEL_BASE_URL=https://ark.cn-beijing.volces.com/api/v3

# Flask配置
FLASK_SECRET_KEY=随机生成的密钥（可以用：openssl rand -hex 32）
WEB_HOST=0.0.0.0
WEB_PORT=5000

# 数据库配置（如果使用PostgreSQL）
DATABASE_URL=postgresql://user:password@host:port/database
```

**如何获取 API Key**:
- 登录火山引擎方舟平台
- 获取 API Key
- 填入 Railway 的环境变量中

### 步骤4: 添加数据库（可选）

如果需要使用数据库功能：

1. 在 Railway 项目页面，点击 "New Service"
2. 选择 "Database"
3. 选择 "PostgreSQL"
4. Railway 会自动创建数据库并生成连接字符串
5. 复制 `DATABASE_URL` 到环境变量中

### 步骤5: 获取访问链接

部署成功后：

1. 在 Railway 项目页面，找到你的 Web 服务
2. 点击 "Generate Domain"
3. 会生成一个类似这样的链接：
   ```
   https://ecommerce-agent-production.up.railway.app
   ```

**这就是你的公网链接！可以分享给任何人使用！** 🎉

### 步骤6: 自定义域名（可选）

如果你想要自己的域名：

1. 在 Railway 项目页面，点击 "Settings"
2. 选择 "Custom Domains"
3. 添加你的域名（如 `agent.yourdomain.com`）
4. 按照提示配置 DNS

## 📱 如何分享给朋友

### 方法1: 直接分享链接

复制 Railway 生成的链接（如 `https://xxx.up.railway.app`），通过微信、QQ、邮件等方式分享给朋友。

### 方法2: 生成二维码

1. 访问：https://www.qrcode-generator.com/
2. 输入你的 Railway 链接
3. 生成二维码
4. 朋友扫码即可访问

### 方法3: 在微信中收藏

1. 在微信中发送链接给自己
2. 点击链接打开
3. 点击右上角 "..." → "收藏"
4. 下次直接从收藏中打开

## 💰 费用说明

Railway 提供免费额度：

- **免费额度**: $5/月
- **包含**:
  - 512 MB RAM
  - 500 小时运行时间/月
  - 1 GB 存储空间

对于个人使用和小范围分享，免费额度完全够用！

如果超出免费额度：
- 超额部分按实际使用量计费
- 一般不会超过几美元/月

## 🔧 常见问题

### Q: 部署失败怎么办？

**A**: 检查以下几点：
1. 确保 `Procfile` 文件存在且格式正确
2. 确保 `requirements-railway.txt` 包含所有依赖
3. 查看部署日志，定位错误信息
4. 确保环境变量配置正确

### Q: 如何更新代码？

**A**:
1. 修改代码
2. 推送到 GitHub
3. Railway 会自动检测并重新部署

### Q: 链接打不开怎么办？

**A**:
1. 检查 Railway 服务是否正在运行
2. 查看健康检查日志
3. 确保端口配置正确（内部端口 5000）
4. 检查防火墙设置

### Q: 如何监控使用情况？

**A**:
1. 在 Railway 项目页面查看 "Metrics"
2. 可以查看 CPU、内存、网络使用情况
3. 查看日志排查问题

## 🚀 进阶配置

### 1. 配置自动缩放

在 `railway.toml` 中配置：

```toml
[deploy]
autoDeploy = true
# 更多配置...
```

### 2. 配置健康检查

Railway 已经在 `railway.toml` 中配置了健康检查 `/health` 端点。

### 3. 配置日志持久化

Railway 会自动保存日志，可以在控制台查看。

## 📚 相关资源

- Railway 官网: https://railway.app/
- Railway 文档: https://docs.railway.app/
- Python 部署指南: https://docs.railway.app/guides/deploy-python

## 🎉 完成！

现在你的电商货源猎手已经部署到公网，可以分享给任何人使用了！

**分享链接示例**:
```
https://你的应用名.up.railway.app
```

朋友点击这个链接就可以在微信、浏览器等任何地方使用你的智能体了！
