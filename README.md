# 🛒 电商货源猎手智能体

## 📖 项目简介

电商货源猎手是一个基于 LangChain 和 LangGraph 构建的智能体，帮助淘宝、拼多多、京东等电商平台的卖家高效寻找潜在热卖商品货源。

### ✨ 核心功能

- 🔍 **市场趋势分析** - 实时搜索市场热销趋势和增长数据
- 🏭 **供应商推荐** - 智能推荐1688、阿里巴巴等优质供应商
- 📊 **竞品分析** - 分析竞争对手情况和市场饱和度
- 🖼️ **图片识别** - 上传产品图片，AI自动识别并分析市场潜力
- 💰 **ROI计算** - 计算投资回报率和利润率
- 📈 **数据持久化** - 保存供应商、产品、趋势数据到数据库
- 📱 **Web界面** - 支持在微信浏览器中使用

### 🎯 适用场景

- 寻找热卖产品货源
- 分析产品市场潜力
- 对比供应商价格和质量
- 计算产品利润和ROI
- 监控市场趋势变化

---

## 🚀 快速开始

### 方式1：本地运行

```bash
# 运行整个流程
bash scripts/local_run.sh -m flow

# 运行单个节点
bash scripts/local_run.sh -m node -n node_name

# 启动HTTP服务
bash scripts/http_run.sh -m http -p 5000
```

### 方式2：启动 Web 服务（微信中使用）

```bash
# 使用启动脚本
./scripts/start_web.sh

# 或手动启动
cd src/web
python3 app.py
```

### 方式3：云端部署（推荐，分享给朋友）

🌐 **一键部署到 Railway/Render，生成公网链接分享给朋友**

👉 [查看云端部署指南](docs/deployment-guide.md)

**快速步骤：**
1. 上传代码到 GitHub：[查看上传指南](docs/upload-to-github.md)
2. 在 Railway 部署项目
3. 配置环境变量
4. 获取公网链接并分享

然后在浏览器访问：http://localhost:5000

### 方式3：部署到云端（分享给朋友）⭐推荐

查看快速部署指南：[docs/QUICKSTART_UPLOAD_DEPLOY.md](./docs/QUICKSTART_UPLOAD_DEPLOY.md)

**简单三步**：
1. 上传项目到 GitHub
2. 部署到 Railway（免费）
3. 获得公网链接，分享给朋友

---

## 📦 项目结构

```
.
├── config                       # 配置目录
│   └── agent_llm_config.json    # 模型配置
├── src                          # 源代码
│   ├── agents/                  # Agent 定义
│   │   └── agent.py             # Agent 实现
│   ├── web/                     # Web 服务
│   │   ├── app.py               # Flask 应用
│   │   └── templates/           # 前端模板
│   │       └── index.html       # Web 界面
│   ├── storage/                 # 数据存储
│   │   ├── database/            # 数据库操作
│   │   │   ├── db.py            # 数据库连接
│   │   │   └── supplier_manager.py  # 供应商管理
│   │   └── memory/              # 短期记忆
│   │       └── memory_saver.py  # 记忆存储
│   ├── tools/                   # 工具定义
│   ├── utils/                   # 工具函数
│   └── main.py                  # 主入口
├── scripts                      # 脚本
│   ├── local_run.sh             # 本地运行脚本
│   ├── http_run.sh              # HTTP 服务脚本
│   ├── start_web.sh             # Web 服务启动脚本
│   └── upload_to_github.sh      # 上传到 GitHub 脚本
├── docs                         # 文档
│   ├── AGENT.md                 # Agent 规范
│   ├── QUICKSTART_UPLOAD_DEPLOY.md  # 快速上传部署指南
│   ├── UPLOAD_TO_GITHUB.md      # 上传到 GitHub 教程
│   ├── DEPLOYMENT_QUICKSTART.md  # 部署快速开始
│   ├── DEPLOY_TO_RAILWAY.md     # Railway 部署教程
│   ├── DEPLOY_TO_RENDER.md      # Render 部署教程
│   ├── DEPLOYMENT_COMPARISON.md # 部署方案对比
│   ├── WEB_SERVICE_GUIDE.md     # Web 服务使用指南
│   └── WEB_QUICKSTART.md        # Web 快速开始
├── tests                        # 测试
├── requirements.txt             # Python 依赖
├── requirements-railway.txt     # 部署依赖（精简）
├── Procfile                     # 部署配置（Railway）
├── railway.toml                 # Railway 配置
└── .gitignore                   # Git 忽略文件
```

---

## 🔧 环境要求

- Python 3.9+
- pip
- PostgreSQL（可选，用于数据持久化）

### 安装依赖

```bash
pip install -r requirements.txt
```

---

## 📱 Web 功能

### 主要特性

- ✅ 实时聊天界面
- ✅ 图片上传和识别
- ✅ 流式响应显示
- ✅ Markdown 格式支持
- ✅ 对话历史管理
- ✅ 移动端适配

### 使用方式

1. **本地访问**
   - 启动服务：`./scripts/start_web.sh`
   - 访问：http://localhost:5000

2. **微信中使用**
   - 确保电脑和手机在同一WiFi
   - 访问局域网IP：http://192.168.x.x:5000
   - 或使用内网穿透工具

3. **分享给朋友**
   - 部署到云端：查看部署文档
   - 获得公网链接
   - 直接分享链接

详细说明：[docs/WEB_SERVICE_GUIDE.md](./docs/WEB_SERVICE_GUIDE.md)

---

## 🌐 云端部署

### 推荐平台

1. **Railway** ⭐⭐⭐⭐⭐
   - 免费 $5/月 额度
   - 性能稳定，不会休眠
   - 部署简单

   详细教程：[docs/DEPLOY_TO_RAILWAY.md](./docs/DEPLOY_TO_RAILWAY.md)

2. **Render** ⭐⭐⭐⭐
   - 完全免费
   - 15分钟后自动休眠
   - 适合小范围使用

   详细教程：[docs/DEPLOY_TO_RENDER.md](./docs/DEPLOY_TO_RENDER.md)

### 快速部署

```bash
# 1. 上传到 GitHub
./scripts/upload_to_github.sh

# 2. 在 Railway/Render 部署
#    按照教程操作即可
```

详细对比：[docs/DEPLOYMENT_COMPARISON.md](./docs/DEPLOYMENT_COMPARISON.md)

---

## 🛠️ Agent 工具

### 搜索工具

- `web_search_tool` - 联网搜索
- `advanced_search_tool` - 高级搜索（支持站点、时间过滤）
- `image_search_tool` - 图片搜索
- `search_1688_tool` - 1688平台搜索
- `search_alibaba_tool` - 阿里巴巴搜索

### 分析工具

- `image_analysis_tool` - 图片分析（多模态）
- `roi_calculator_tool` - ROI计算
- `competitor_analysis_tool` - 竞品分析
- `trend_analysis_tool` - 趋势分析
- `supplier_evaluation_tool` - 供应商评估

### 数据库工具

- `save_supplier_to_db` - 保存供应商
- `save_product_to_db` - 保存产品
- `query_suppliers_from_db` - 查询供应商
- `save_trend_to_db` - 保存趋势
- `query_trends_from_db` - 查询趋势

### 用户工具

- `save_user_preference` - 保存用户偏好
- `get_user_preference` - 获取用户偏好
- `smart_recommend_products` - 智能推荐
- `get_notifications` - 获取通知
- `create_trend_notification` - 创建通知

---

## 🔑 环境变量

### 必需变量

```bash
# API 配置
COZE_WORKLOAD_IDENTITY_API_KEY=你的API密钥
COZE_INTEGRATION_MODEL_BASE_URL=https://ark.cn-beijing.volces.com/api/v3

# Flask 配置
FLASK_SECRET_KEY=随机生成的密钥
WEB_HOST=0.0.0.0
WEB_PORT=5000
```

### 可选变量

```bash
# 数据库配置
DATABASE_URL=postgresql://user:password@host:port/database

# Web 调试模式
WEB_DEBUG=False
```

---

## 📝 使用示例

### 示例1：搜索市场趋势

```
用户：帮我搜索2024年面膜的市场趋势
```

Agent 会返回：
- 当前市场规模
- 增长率数据
- 热销产品类型
- 推荐关键词

### 示例2：图片分析

上传产品图片后：

```
用户：帮我分析这个产品的市场潜力
```

Agent 会：
- 识别产品类型
- 分析产品特征
- 评估市场潜力
- 推荐供应商

### 示例3：计算ROI

```
用户：进货价50元，售价120元，物流成本10元，帮我算一下ROI
```

Agent 会返回详细的利润分析和ROI计算结果。

---

## 📚 文档

### 快速开始

- [快速上传部署指南](./docs/QUICKSTART_UPLOAD_DEPLOY.md)
- [上传到 GitHub 教程](./docs/UPLOAD_TO_GITHUB.md)
- [部署快速开始](./docs/DEPLOYMENT_QUICKSTART.md)

### 部署文档

- [Railway 部署教程](./docs/DEPLOY_TO_RAILWAY.md)
- [Render 部署教程](./docs/DEPLOY_TO_RENDER.md)
- [部署方案对比](./docs/DEPLOYMENT_COMPARISON.md)

### Web 服务

- [Web 服务使用指南](./docs/WEB_SERVICE_GUIDE.md)
- [Web 快速开始](./docs/WEB_QUICKSTART.md)

### Agent 规范

- [Agent 规范](./docs/AGENT.md)

---

## 🆘 常见问题

### Q: 如何获取 API Key？

访问火山引擎方舟平台：https://console.volcengine.com/ark

### Q: 部署失败怎么办？

查看对应的部署文档中的故障排查部分。

### Q: 可以在微信中使用吗？

可以！详见 [Web 服务使用指南](./docs/WEB_SERVICE_GUIDE.md)

### Q: 如何分享给朋友？

部署到云端后，会获得公网链接，可以直接分享。详见 [部署快速开始](./docs/DEPLOYMENT_QUICKSTART.md)

---

## 📄 许可证

本项目仅供学习和个人使用，商业使用请确保遵守相关法律法规。

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📞 联系方式

如有问题，请提交 Issue 或联系维护者。

---

## 🎉 开始使用

选择你的方式开始使用：

1. **本地运行** → 查看快速开始
2. **启动 Web 服务** → `./scripts/start_web.sh`
3. **部署到云端** → 查看部署文档

**现在就开始吧！** 🚀
