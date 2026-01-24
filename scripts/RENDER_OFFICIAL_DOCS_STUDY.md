# Render 官方文档学习笔记

## 1. 部署流程理解

### 1.1 部署生命周期

1. **Push 代码到 GitHub**
2. **Render 检测到推送**
3. **构建阶段 (Build)**
   - 拉取代码
   - 运行 Build Command
   - 构建 Docker 镜像
4. **部署阶段 (Deploy)**
   - 启动容器
   - 运行 Start Command
   - 健康检查

### 1.2 关键配置

**Docker Runtime**:
```dockerfile
# 必须暴露端口
EXPOSE 5000

# 环境变量
ENV PORT=5000

# 启动命令
CMD ["python", "src/web/app.py"]
```

**重要**:
- Render 会自动注入 `PORT` 环境变量
- 应用必须监听 `0.0.0.0` 而不是 `127.0.0.1`

## 2. 环境变量管理

### 2.1 环境变量优先级

1. Render 控制台配置的环境变量（优先级最高）
2. Dockerfile 中的 ENV
3. 代码中的默认值

### 2.2 Secret 类型

- Secret 类型的环境变量值是隐藏的
- 创建后无法查看值，只能覆盖
- 用于敏感信息（API Key、密码等）

### 2.3 环境变量配置示例

```bash
# Render 控制台中配置
COZE_WORKSPACE_PATH=/workspace/projects
COZE_WORKLOAD_IDENTITY_API_KEY=your-api-key
PORT=5000
```

## 3. 日志查看

### 3.1 日志类型

1. **Build Logs** - 构建阶段的日志
2. **Deploy Logs** - 部署阶段的日志
3. **Application Logs** - 运行时的日志

### 3.2 查看方式

```bash
# 访问 Render 控制台
# 选择服务 -> Logs 标签
# 可以查看实时日志和历史日志
```

### 3.3 关键日志信息

```
==> Building...
==> Deploying...
==> Your service is live 🎉
```

## 4. 常见问题排查

### 4.1 构建失败

**检查项**:
1. requirements.txt 格式是否正确
2. 依赖版本是否兼容
3. Dockerfile 语法是否正确
4. 文件路径是否正确

### 4.2 部署失败

**检查项**:
1. Start Command 是否正确
2. 端口是否正确
3. 环境变量是否配置
4. 依赖是否安装

### 4.3 运行时错误

**检查项**:
1. 应用日志
2. 环境变量
3. 依赖版本
4. 代码逻辑

## 5. 我的问题分析

### 5.1 历史问题回顾

1. **SDK 版本反复问题**
   - 本地环境: coze-coding-dev-sdk==0.5.5
   - Dockerfile 强制: coze-coding-dev-sdk==0.5.3
   - requirements.txt: 被自动更新

2. **响应长度为 0 问题**
   - 后端日志: `INFO:__main__:响应完成，长度: 0`
   - 本地测试: 响应长度 345
   - 环境差异导致？

### 5.2 可能的原因

1. **环境变量差异**
   - Render 环境缺少必要的环境变量
   - API Key 配置不正确

2. **依赖版本不一致**
   - Docker 构建时的依赖版本与本地不一致
   - SDK 版本问题

3. **网络问题**
   - Render 环境网络连接问题
   - API 调用超时

## 6. 系统性排查计划

### 6.1 第一步：查看完整日志

1. 访问 Render 控制台
2. 选择服务
3. 点击 Logs 标签
4. 查看最新的完整日志
5. 特别关注：
   - 构建日志（是否有错误）
   - 部署日志（是否成功）
   - 应用日志（运行时错误）

### 6.2 第二步：对比环境

**本地环境**:
```bash
pip list | grep coze-coding-dev-sdk
# 输出: coze-coding-dev-sdk  0.5.3

python --version
# 输出: Python 3.12.x
```

**Render 环境**:
```dockerfile
# 查看 Dockerfile 中的验证步骤
RUN pip show coze-coding-dev-sdk | grep Version
```

### 6.3 第三步：环境变量检查

**必需的环境变量**:
1. `COZE_WORKLOAD_IDENTITY_API_KEY` - Coze 平台 API Key
2. `ARK_API_KEY` - 火山方舟 API Key（如果使用）
3. `PORT` - 端口（Render 自动注入）

### 6.4 第四步：API 调用测试

在代码中添加更详细的日志：

```python
logger.info(f"API Key: {api_key[:10]}...")
logger.info(f"Base URL: {base_url}")
logger.info(f"Model: {model_name}")
```

## 7. 行动计划

### 7.1 立即执行

1. **查看 Render 完整日志**
   - 访问 https://dashboard.render.com
   - 找到服务: ecommerce-supply-scout-1
   - 查看 Logs 标签
   - 记录完整的日志内容

2. **对比本地和 Render 环境**
   - 记录本地 SDK 版本
   - 记录 Render SDK 版本
   - 对比差异

3. **检查环境变量**
   - 在 Render 控制台查看环境变量
   - 确认 API Key 是否正确

### 7.2 根据日志结果决定

**情况 1: SDK 版本错误**
- 如果 Render 安装的是 0.5.5
- 检查 Dockerfile 中的强制安装命令
- 确认是否正确执行

**情况 2: API Key 错误**
- 检查环境变量配置
- 确认 API Key 格式
- 测试 API Key 有效性

**情况 3: 网络问题**
- 检查 Render 日志中的网络错误
- 测试 API 连通性

## 8. 总结

**我之前的问题**:
1. 没有仔细查看 Render 日志
2. 没有系统性地排查问题
3. 没有对比环境差异
4. 没有理解 Render 的部署机制

**正确的做法**:
1. 先看日志，了解问题本质
2. 对比环境，找出差异
3. 系统性排查，逐步缩小范围
4. 根据证据，精准修复

---

**现在需要您提供 Render 的完整日志！**
