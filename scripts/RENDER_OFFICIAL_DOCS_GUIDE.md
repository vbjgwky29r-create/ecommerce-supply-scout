# Render 环境变量配置 - 基于官方文档

## 📚 Render 官方文档说明

根据 Render 官方文档：https://render.com/docs/configure-environment-variables

### 环境变量类型

Render 支持两种类型的环境变量：

1. **Environment Variables**（环境变量）
   - 用于普通配置
   - 值可见，可以编辑
   - 例如：`PORT`、`NODE_ENV` 等

2. **Secrets**（密钥）
   - 用于敏感信息（API Key、密码等）
   - 值是隐藏的，只能看到 Key
   - 例如：`DATABASE_URL`、`API_KEY` 等

### 重要说明

**Secrets 的值是隐藏的**，这是正常的设计：
- ✅ 这是安全特性，防止敏感信息泄露
- ✅ 即使您看不到值，变量仍然存在且可用
- ✅ 您可以编辑（覆盖）Secrets 的值

---

## 🚀 针对您的问题

您提到**看不到全部的环境变量**，这很正常：

### 可能的情况

1. **Secrets 类型的变量值是隐藏的**
   - 这是安全特性
   - 您可以看到 Key，但看不到 Value
   - 例如：`OPENAI_API_KEY` 可能是 Secret，值被隐藏了

2. **变量在 render.yaml 中定义**
   - 如果您的项目有 `render.yaml` 文件
   - 环境变量可能在文件中定义
   - 在 Web 界面中可能不显示

3. **变量在 Dockerfile 中定义**
   - 如果使用了 `ENV` 指令
   - 这些变量在 Web 界面中可能不显示

---

## ✅ 解决方案（基于官方文档）

### 方案 1: 覆盖环境变量（推荐）

由于 Render 支持覆盖环境变量，您可以直接添加新的变量来覆盖已有的变量。

#### 操作步骤

**添加以下变量，覆盖错误的配置**：

1. **覆盖 OPENAI_API_KEY**
   - 点击 "Add Environment Variable"
   - Key: `OPENAI_API_KEY`
   - Value: `""` （空字符串）
   - Type: 选择 **Secret**（因为它是敏感信息）

   **注意**：覆盖为空值后，应用不会使用这个变量。

2. **覆盖 OPENAI_BASE_URL**
   - 点击 "Add Environment Variable"
   - Key: `OPENAI_BASE_URL`
   - Value: `https://integration.coze.cn/api/v3`
   - Type: 选择 **Environment Variable**（非敏感信息）

3. **添加豆包变量**（如果还没有）

   **变量 1**:
   - Key: `COZE_WORKLOAD_IDENTITY_API_KEY`
   - Value: 您的火山方舟 API Key
   - Type: **Secret**

   **变量 2**:
   - Key: `COZE_INTEGRATION_MODEL_BASE_URL`
   - Value: `https://integration.coze.cn/api/v3`
   - Type: **Environment Variable**

   **变量 3**:
   - Key: `COZE_WORKSPACE_PATH`
   - Value: `/app`
   - Type: **Environment Variable**

#### 为什么这样有效？

根据 Render 官方文档：
- ✅ 后添加的变量会覆盖先添加的同名变量
- ✅ 应用启动时会使用最新的变量值
- ✅ 即使旧变量存在，也会被新值覆盖

---

### 方案 2: 使用 render.yaml（高级）

如果您的项目有 `render.yaml` 文件，可以在文件中定义环境变量。

#### 示例 render.yaml

```yaml
services:
  - type: web
    name: ecommerce-supply-scout
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python src/main.py
    envVars:
      - key: COZE_WORKLOAD_IDENTITY_API_KEY
        sync: false  # 不在 Web 界面显示
      - key: COZE_INTEGRATION_MODEL_BASE_URL
        value: https://integration.coze.cn/api/v3
        sync: false
      - key: COZE_WORKSPACE_PATH
        value: /app
        sync: false
```

#### 说明

- `sync: false` 表示不在 Web 界面显示此变量
- 这样可以避免 Web 界面中显示的混乱
- 适合配置固定不变的变量

---

### 方案 3: 检查 Dockerfile

如果您的 `Dockerfile` 中有 `ENV` 指令，这些变量会在容器启动时设置。

#### 示例 Dockerfile

```dockerfile
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 设置环境变量（可选）
ENV COZE_WORKSPACE_PATH=/app
ENV COZE_INTEGRATION_MODEL_BASE_URL=https://integration.coze.cn/api/v3

# 启动应用
CMD ["python", "src/main.py"]
```

#### 注意

- Dockerfile 中的 ENV 指令设置的环境变量会优先于 render.yaml 和 Web 界面的变量
- 如果使用了 Dockerfile，建议在代码中检查环境变量是否存在

---

### 方案 4: 修改代码，强制使用豆包配置

修改 `src/agents/agent.py`，强制使用豆包配置，忽略 OpenAI 变量。

#### 代码修改

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
    
    # 强制使用豆包配置
    api_key = os.getenv("COZE_WORKLOAD_IDENTITY_API_KEY")
    base_url = os.getenv("COZE_INTEGRATION_MODEL_BASE_URL")
    
    # 设置默认值（如果环境变量不存在）
    if not base_url:
        base_url = "https://integration.coze.cn/api/v3"
        import logging
        logging.warning("COZE_INTEGRATION_MODEL_BASE_URL 未设置，使用默认值")
    
    if not api_key:
        raise ValueError(
            "缺少必需的环境变量: COZE_WORKLOAD_IDENTITY_API_KEY\n"
            "请在 Render 环境变量中配置该变量"
        )
    
    # 创建 LLM 实例
    llm = ChatOpenAI(
        model=cfg['config'].get("model"),
        api_key=api_key,  # 使用豆包 API Key
        base_url=base_url,  # 使用豆包 API 地址
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

#### 优点

- 即使有 `OPENAI_API_KEY` 环境变量，也不会使用
- 强制使用豆包配置
- 提供清晰的错误提示

---

## 🎯 推荐操作流程

### 步骤 1: 添加覆盖变量（最简单）

在 Render Web 界面中：

1. 点击 "Add Environment Variable"
2. 添加以下变量：

   ```
   Key: OPENAI_API_KEY
   Value: "" (空字符串)
   Type: Secret
   ```

   ```
   Key: OPENAI_BASE_URL
   Value: https://integration.coze.cn/api/v3
   Type: Environment Variable
   ```

3. 确保豆包变量已配置：

   ```
   Key: COZE_WORKLOAD_IDENTITY_API_KEY
   Value: 您的火山方舟 API Key
   Type: Secret
   ```

   ```
   Key: COZE_INTEGRATION_MODEL_BASE_URL
   Value: https://integration.coze.cn/api/v3
   Type: Environment Variable
   ```

   ```
   Key: COZE_WORKSPACE_PATH
   Value: /app
   Type: Environment Variable
   ```

### 步骤 2: 保存并重启

1. 点击 "Save Changes"
2. 等待服务自动重启（2-5 分钟）
3. 等待状态变为 "Live"

### 步骤 3: 测试验证

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
   - `COZE_WORKLOAD_IDENTITY_API_KEY`
   - `integration.coze.cn`
   - `Error`
   - `Exception`

### 使用诊断脚本

如果 Render 支持在服务器上运行脚本，可以执行：

```bash
cd /app
python scripts/diagnose_environment.py
```

---

## 📝 Render 环境变量最佳实践

根据 Render 官方文档的建议：

### 1. 使用 Secrets 存储敏感信息

- ✅ API Keys
- ✅ 数据库密码
- ✅ 第三方服务凭证

### 2. 使用 Environment Variables 存储非敏感信息

- ✅ 配置文件路径
- ✅ 端口号
- ✅ 环境标识（dev、prod）

### 3. 使用 render.yaml 定义固定变量

- ✅ 不变的配置
- ✅ 服务间的配置共享
- ✅ 版本控制

### 4. 使用环境变量而非硬编码

- ✅ 便于不同环境配置
- ✅ 安全性更高
- ✅ 灵活性更强

---

## ✅ 总结

### 问题澄清

根据 Render 官方文档：

1. **Secrets 类型的变量值是隐藏的**（正常设计）
2. **后添加的变量会覆盖先添加的同名变量**
3. **可以使用 render.yaml 定义环境变量**
4. **可以在 Dockerfile 中使用 ENV 指令**

### 推荐方案

**方案 1: 覆盖环境变量**（最简单，推荐）

添加新变量来覆盖已有的变量：
- 添加 `OPENAI_API_KEY` 为空值
- 添加 `OPENAI_BASE_URL` 指向豆包地址
- 确保豆包相关变量已正确配置

### 下一步

1. 按照方案 1 的步骤操作
2. 保存并重启服务
3. 测试应用是否正常

---

**现在您可以按照方案 1 的步骤操作了！** 🚀

**关键点**：Render 支持覆盖环境变量，后添加的变量会覆盖先添加的同名变量。
