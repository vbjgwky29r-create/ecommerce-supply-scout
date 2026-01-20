# 🚀 快速部署到云端 - 分享给朋友使用

## 🎯 你的目标

**想要一个可以直接分享给朋友的链接，让他们在微信中使用电商货源猎手！**

## ✅ 推荐方案（按优先级）

### 🥇 方案1: Railway（最推荐）

**特点**: 免费、稳定、快速、永久在线

**5分钟部署**:
1. 访问 https://railway.app/ 注册账号
2. 连接你的 GitHub 仓库
3. 配置环境变量（API Key等）
4. 等待部署完成
5. 获得链接: `https://你的应用名.up.railway.app`

**详细教程**: [点击查看](./DEPLOY_TO_RAILWAY.md)

---

### 🥈 方案2: Render

**特点**: 完全免费、部署简单

**5分钟部署**:
1. 访问 https://render.com/ 注册账号
2. 连接 GitHub 仓库
3. 创建 Web Service
4. 配置环境变量
5. 获得链接: `https://你的应用名.onrender.com`

**详细教程**: [点击查看](./DEPLOY_TO_RENDER.md)

**注意**: 15分钟无访问会自动休眠，有访问时自动唤醒

---

### 🥉 方案3: 购买云服务器

**特点**: 完全掌控、稳定快速、适合长期运营

**费用**: 约¥100-300/年

**适合**: 有一定技术基础，想要长期运营

**推荐云服务商**:
- 腾讯云: https://cloud.tencent.com/
- 阿里云: https://www.aliyun.com/
- 华为云: https://www.huaweicloud.com/

---

### ⚡ 方案4: Ngrok（临时使用）

**特点**: 超级简单、无需注册云平台

**1分钟搞定**:
```bash
# 1. 下载 ngrok
# 2. 运行:
ngrok http 5000

# 3. 复制生成的链接
https://random-name.ngrok-free.app
```

**注意**: 每次重启链接会变化，适合临时测试

---

## 📱 部署成功后

### 你会得到这样的链接：

```
https://ecommerce-agent.up.railway.app
https://ecommerce-agent.onrender.com
https://123.45.67.89:5000
https://random-name.ngrok-free.app
```

### 如何分享给朋友：

1. **直接复制链接**
   - 通过微信、QQ、邮件发送

2. **生成二维码**
   - 访问: https://www.qrcode-generator.com/
   - 输入链接生成二维码
   - 朋友扫码访问

3. **在微信中收藏**
   - 发送给自己
   - 点击打开
   - 收藏备用

---

## 🎯 我的建议

### 想要长期稳定分享？→ **选 Railway** ✅

- 免费额度够用
- 不会自动休眠
- 访问速度快
- 部署简单

**立即开始**: [Railway 部署教程](./DEPLOY_TO_RAILWAY.md)

---

### 只想偶尔分享？→ **选 Render** ✅

- 完全免费
- 部署简单
- 15分钟后会休眠（有访问自动唤醒）

**立即开始**: [Render 部署教程](./DEPLOY_TO_RENDER.md)

---

### 临时测试？→ **选 Ngrok** ✅

- 一条命令搞定
- 无需注册

**立即开始**:
```bash
ngrok http 5000
```

---

## 📊 方案对比

| 方案 | 费用 | 难度 | 稳定性 | 速度 | 推荐度 |
|------|------|------|--------|------|--------|
| Railway | 免费 | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Render | 免费 | ⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 云服务器 | ¥100/年 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Ngrok | 免费/付费 | ⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |

---

## ⚙️ 部署前准备

### 必需文件（已创建✅）:
- ✅ `Procfile` - 告诉平台如何启动
- ✅ `railway.toml` - Railway 配置
- ✅ `requirements-railway.txt` - 依赖列表
- ✅ `src/web/app.py` - Web 服务
- ✅ `src/agents/agent.py` - Agent 代码

### 必需环境变量（部署时配置）:
```
COZE_WORKLOAD_IDENTITY_API_KEY=你的API密钥
COZE_INTEGRATION_MODEL_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
FLASK_SECRET_KEY=随机密钥
```

---

## 🔑 如何获取 API Key？

1. 登录火山引擎方舟平台: https://console.volcengine.com/ark
2. 进入 API Key 管理
3. 创建新的 API Key
4. 复制并保存（部署时使用）

---

## 🎉 开始部署吧！

我推荐你从 **Railway** 开始，因为：
- ✅ 最稳定
- ✅ 最简单
- ✅ 免费额度最慷慨
- ✅ 适合长期分享

**立即开始**: [Railway 部署教程](./DEPLOY_TO_RAILWAY.md)

---

## ❓ 需要帮助？

- 遇到问题？查看对应平台的详细教程
- 不确定选哪个？参考上面的对比表
- 需要更多帮助？随时询问我！

---

## 🚀 5分钟后

你就能把链接分享给朋友了！

**分享链接示例**:
```
https://ecommerce-agent.up.railway.app
```

朋友点击链接，就能在微信中使用你的智能体了！🎉
