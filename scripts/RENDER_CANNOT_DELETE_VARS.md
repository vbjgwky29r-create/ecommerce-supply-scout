# Render 无法删除环境变量的解决方案

## 🚨 问题说明

Render 环境变量列表**不完整**，无法看到全部的已有变量，导致：
- ❌ 无法删除 `OPENAI_API_KEY` 等错误的变量
- ✅ 只能添加新的环境变量

---

## 💡 解决方案

### 方案 1: 覆盖已有变量（推荐）

如果无法删除，可以**覆盖**已有变量，使其失效。

#### 操作步骤

**添加以下环境变量，覆盖错误的配置**：

1. **添加 `OPENAI_API_KEY` 为空值**
   - Key: `OPENAI_API_KEY`
   - Value: ` ""` （空字符串）
   - 说明: 覆盖为空值，使其失效

2. **添加 `OPENAI_BASE_URL` 指向正确的地址**
   - Key: `OPENAI_BASE_URL`
   - Value: `https://integration.coze.cn/api/v3`
   - 说明: 指向豆包的 API 地址

3. **确保豆包相关变量已正确配置**
   - Key: `COZE_WORKLOAD_IDENTITY_API_KEY`
   - Value: 您的火山方舟 API Key
   - Type: Secret

4. **确保豆包 API 地址已配置**
   - Key: `COZE_INTEGRATION_MODEL_BASE_URL`
   - Value: `https://integration.coze.cn/api/v3`
   - Type: Plain Text

5. **确保工作目录已配置**
   - Key: `COZE_WORKSPACE_PATH`
   - Value: `/app`
   - Type: Plain Text

#### 为什么这样有效？

- 应用优先使用 `COZE_*` 环境变量
- 即使 `OPENAI_API_KEY` 存在，也会被空值覆盖
- `OPENAI_BASE_URL` 指向豆包地址，确保请求发送到正确的位置

---

### 方案 2: 使用 Render CLI（高级用户）

如果可以使用 Render 命令行工具，可以通过 CLI 删除变量。

#### 前提条件

1. 安装 Render CLI
2. 登录 Render 账号

#### 操作步骤

```bash
# 1. 登录 Render
render login

# 2. 列出所有环境变量
render env ls --service <your-service-id>

# 3. 删除指定的变量
render env rm OPENAI_API_KEY --service <your-service-id>
render env rm OPENAI_ORGANIZATION --service <your-service-id>
render env rm OPENAI_BASE_URL --service <your-service-id>
```

#### 获取 Service ID

1. 访问 Render 控制台
2. 点击您的服务
3. 查看浏览器地址栏
4. Service ID 在 URL 中，例如：
   `https://dashboard.render.com/web/services/<service-id>/...`

---

### 方案 3: 联系 Render 支持

如果以上方案都无法解决，联系 Render 技术支持。

#### 联系方式

1. **Render 官方支持**: https://render.com/support
2. **GitHub Issues**: https://github.com/render/render/issues
3. **Twitter**: @render
4. **Discord**: Render Discord 社区

#### 反馈内容

```
问题：Render 环境变量列表不完整

描述：
在 Environment 页面中，环境变量列表无法显示全部的已有变量，导致无法删除某些环境变量。

截图：[提供截图]

期望：
- 能够看到所有环境变量
- 能够删除任意环境变量

服务信息：
- Service ID: [您的 Service ID]
- Service Name: [您的服务名称]
```

---

## ✅ 推荐操作（方案 1）

### 立即执行

#### 1. 添加覆盖变量

在 Render 环境变量页面，添加以下变量：

**变量 1: OPENAI_API_KEY**
- Key: `OPENAI_API_KEY`
- Value: `""` （空字符串，不包含引号）
- Type: Plain Text

**变量 2: OPENAI_BASE_URL**
- Key: `OPENAI_BASE_URL`
- Value: `https://integration.coze.cn/api/v3`
- Type: Plain Text

#### 2. 添加豆包变量（如果还没有）

**变量 3: COZE_WORKLOAD_IDENTITY_API_KEY**
- Key: `COZE_WORKLOAD_IDENTITY_API_KEY`
- Value: 您的火山方舟 API Key
- Type: Secret

**变量 4: COZE_INTEGRATION_MODEL_BASE_URL**
- Key: `COZE_INTEGRATION_MODEL_BASE_URL`
- Value: `https://integration.coze.cn/api/v3`
- Type: Plain Text

**变量 5: COZE_WORKSPACE_PATH**
- Key: `COZE_WORKSPACE_PATH`
- Value: `/app`
- Type: Plain Text

#### 3. 保存并重启

1. 点击 "Save Changes"
2. 等待服务自动重启（2-5 分钟）
3. 等待状态变为 "Live"

#### 4. 测试验证

1. 访问应用 URL
2. 输入: `你好`
3. 确认正常回复

---

## 🔍 验证配置

### 检查应用日志

如果仍然报错，查看日志：

1. 在 Render 控制台，点击 "Logs" 标签
2. 查看最新的日志
3. 搜索关键词：
   - `Error`
   - `API key`
   - `401`
   - `OPENAI`

### 可能的错误和解决方案

#### 错误 1: 仍然显示 OpenAI API key 错误

**原因**: 应用仍在使用 OpenAI API key

**解决方案**:
1. 确认已添加 `OPENAI_API_KEY` 为空值
2. 确认已添加 `OPENAI_BASE_URL` 指向豆包地址
3. 重启服务
4. 查看日志，确认使用了正确的 API

#### 错误 2: 应用启动失败

**原因**: 环境变量配置错误

**解决方案**:
1. 检查所有变量的 Key 是否正确
2. 检查所有变量的 Value 是否正确
3. 检查 API Key 是否有效
4. 查看详细日志，定位具体错误

---

## 📝 代码层面优化

如果以上方法都无法解决，可以从代码层面优化，使应用不依赖 OpenAI 环境变量。

### 修改 `src/agents/agent.py`

在代码中强制使用豆包配置，忽略 OpenAI 变量：

```python
def build_agent(ctx=None):
    workspace_path = os.getcwd()
    config_path = os.path.join(workspace_path, LLM_CONFIG)
    
    if not os.path.exists(config_path) and os.getenv("COZE_WORKSPACE_PATH"):
        workspace_path = os.getenv("COZE_WORKSPACE_PATH")
        config_path = os.path.join(workspace_path, LLM_CONFIG)
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(
            f"配置文件未找到: {config_path}\n"
            f"当前工作目录: {os.getcwd()}\n"
            f"COZE_WORKSPACE_PATH: {os.getenv('COZE_WORKSPACE_PATH')}\n"
        )
    
    with open(config_path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    
    # 强制使用豆包配置，忽略 OpenAI 变量
    api_key = os.getenv("COZE_WORKLOAD_IDENTITY_API_KEY")
    base_url = os.getenv("COZE_INTEGRATION_MODEL_BASE_URL")
    
    # 如果豆包变量不存在，使用默认值
    if not base_url:
        base_url = "https://integration.coze.cn/api/v3"
        logger.warning("COZE_INTEGRATION_MODEL_BASE_URL 未设置，使用默认值")
    
    if not api_key:
        raise ValueError(
            "缺少必需的环境变量: COZE_WORKLOAD_IDENTITY_API_KEY\n"
            "请在 Render 环境变量中配置该变量"
        )
    
    llm = ChatOpenAI(
        model=cfg['config'].get("model"),
        api_key=api_key,
        base_url=base_url,
        temperature=cfg['config'].get('temperature', 0.7),
        streaming=True,
        timeout=cfg['config'].get('timeout', 600),
        extra_body={
            "thinking": {
                "type": cfg['config'].get('thinking', 'disabled')
            }
        },
        default_headers=default_headers(ctx) if ctx else {}
    )
    
    # ... 后续代码
```

### 优点

- 即使有 `OPENAI_API_KEY` 环境变量，也不会使用
- 强制使用豆包配置
- 提供清晰的错误提示

---

## 🎯 总结

### 问题根源

Render 环境变量列表**不完整**，导致无法删除已有变量。

### 推荐方案

**方案 1: 覆盖已有变量**（最简单）

1. 添加 `OPENAI_API_KEY` 为空值
2. 添加 `OPENAI_BASE_URL` 指向豆包地址
3. 确保豆包相关变量已正确配置
4. 保存并重启

### 其他方案

- **方案 2**: 使用 Render CLI 删除变量
- **方案 3**: 联系 Render 支持
- **方案 4**: 修改代码强制使用豆包配置

### 下一步

1. 尝试方案 1（覆盖变量）
2. 如果仍有问题，尝试方案 2（CLI）
3. 如果仍然无法解决，联系 Render 支持

---

**现在您可以按照方案 1 的步骤操作了！** 🚀
