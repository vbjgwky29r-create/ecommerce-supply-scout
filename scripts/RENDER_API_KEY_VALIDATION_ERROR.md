# 豆包 API Key 验证失败 - 解决方案

## 🚨 错误说明

错误信息：
```
❌ 处理失败: code=190000007 message=no permission {msg}
cause=token validation failed: failed to parse token: token contains an invalid number of segments
```

**含义**：
- API key 的格式不正确
- API key 无效
- API key 已过期

---

## 🔍 可能的原因

### 1. API Key 格式不正确

火山方舟 API Key 应该是 **Base64 编码的字符串**，格式类似：
```
aHJkd25NSmhSWENDQzdnZ1JhVnJ0b2ZwdHRtYnI0eGJxNnN2cH...
```

**错误格式**：
- ❌ `sk-xxxxxxxxxxxx`（这是 OpenAI 的格式）
- ❌ `1234567890`（纯数字）
- ❌ `abc123`（太短）
- ❌ 空字符串或缺失

### 2. API Key 已过期

火山方舟的 API Key 可能会过期，需要重新生成。

### 3. API Key 配置错误

环境变量配置错误：
- ❌ 变量名拼写错误（如 `COZE_WORKLOAD_IDENTITY_API_KEYS` 多了一个 s）
- ❌ 变量名大小写错误
- ❌ Value 中有多余的空格或换行符

---

## ✅ 解决方案

### 方案 1: 重新生成并配置 API Key（推荐）

#### 步骤 1: 登录火山方舟控制台

1. 访问：https://console.volcengine.com/ark
2. 登录您的火山引擎账号

#### 步骤 2: 进入 API Key 管理

1. 在左侧导航栏，找到 **"API Key 管理"**
2. 点击进入

#### 步骤 3: 创建新的 API Key

1. 点击 **"创建 API Key"** 按钮
2. 选择权限范围（通常选择 **"全部权限"**）
3. 点击 **"确定"**

#### 步骤 4: 复制 API Key

**重要**：API Key **只显示一次**，请立即复制并保存！

格式应该类似于：
```
aHJkd25NSmhSWENDQzdnZ1JhVnJ0b2ZwdHRtYnI0eGJxNnN2cH...
```

#### 步骤 5: 配置到 Render

1. 访问 Render 控制台
2. 找到您的服务
3. 点击 "Environment" 标签
4. 找到 `COZE_WORKLOAD_IDENTITY_API_KEY` 变量
5. 点击编辑按钮
6. 删除旧的 API Key
7. 粘贴新的 API Key
8. 点击保存

**注意**：
- ✅ 直接粘贴，不要添加引号
- ✅ 不要添加空格或换行符
- ✅ 确保变量名是 `COZE_WORKLOAD_IDENTITY_API_KEY`（大写）

#### 步骤 6: 重启服务

1. 点击 "Save Changes"
2. 等待服务自动重启（2-5 分钟）
3. 等待状态变为 "Live"

#### 步骤 7: 测试验证

1. 访问应用 URL
2. 输入: `你好`
3. 确认正常回复

---

### 方案 2: 验证 API Key 格式

#### 检查方法

1. 访问 Render 控制台
2. 找到 `COZE_WORKLOAD_IDENTITY_API_KEY` 变量
3. 查看 Value 的长度（应该比较长，通常 100+ 字符）
4. 确认没有多余的字符

#### 正确格式示例

✅ **正确**：
```
aHJkd25NSmhSWENDQzdnZ1JhVnJ0b2ZwdHRtYnI0eGJxNnN2cH...
```

❌ **错误**：
```
sk-1234567890
```
```
1234567890
```
```
""
```
（空字符串）

---

### 方案 3: 检查环境变量配置

#### 检查变量名

确认变量名完全正确：

✅ **正确**：
```
COZE_WORKLOAD_IDENTITY_API_KEY
```

❌ **错误**：
```
COZE_WORKLOAD_IDENTITY_API_KEYS （多了一个 s）
coze_workload_identity_api_key （全部小写）
Coze_Workload_Identity_Api_Key （大小写混合）
```

#### 检查变量值

1. 确认 Value 不为空
2. 确认 Value 中没有多余的空格
3. 确认 Value 中没有换行符
4. 确认 Value 是完整的 API Key

---

### 方案 4: 查看详细日志

#### 步骤

1. 访问 Render 控制台
2. 找到您的服务
3. 点击 "Logs" 标签
4. 查看最新的日志
5. 搜索关键词：
   - `token validation failed`
   - `190000007`
   - `no permission`
   - `COZE_WORKLOAD_IDENTITY_API_KEY`

#### 可能的日志

**错误日志示例**：
```
Error: token validation failed: failed to parse token: token contains an invalid number of segments
API Key: aHJkd25NSmhSWENDQzdn...
```

**正常日志示例**：
```
INFO: Using COZE_WORKLOAD_IDENTITY_API_KEY
INFO: Connecting to https://integration.coze.cn/api/v3
```

---

## 🔧 本地测试

### 方法 1: 使用诊断脚本

在本地环境中运行诊断脚本：

```bash
python scripts/diagnose_environment.py
```

检查输出：
- ✅ `COZE_WORKLOAD_IDENTITY_API_KEY` 是否配置
- ✅ API Key 的前 20 个字符是否显示

### 方法 2: 手动测试 API Key

创建测试脚本 `test_api_key.py`：

```python
import os
from langchain_openai import ChatOpenAI

# 获取 API Key
api_key = os.getenv("COZE_WORKLOAD_IDENTITY_API_KEY")
base_url = os.getenv("COZE_INTEGRATION_MODEL_BASE_URL", "https://integration.coze.cn/api/v3")

print(f"API Key: {api_key[:20]}..." if api_key else "API Key: 未设置")
print(f"Base URL: {base_url}")

# 测试连接
try:
    llm = ChatOpenAI(
        model="doubao-seed-1-8-251228",
        api_key=api_key,
        base_url=base_url,
        temperature=0.7,
    )
    
    # 发送测试消息
    response = llm.invoke("你好")
    print(f"✅ 测试成功: {response.content[:50]}...")
    
except Exception as e:
    print(f"❌ 测试失败: {e}")
```

运行测试：
```bash
python test_api_key.py
```

---

## 📋 故障排除清单

完成配置后，确认：

### API Key 检查
- [ ] API Key 是从火山方舟控制台获取的
- [ ] API Key 是 Base64 编码的字符串
- [ ] API Key 长度足够（100+ 字符）
- [ ] API Key 没有过期
- [ ] API Key 没有被删除

### 环境变量检查
- [ ] 变量名是 `COZE_WORKLOAD_IDENTITY_API_KEY`
- [ ] 变量名的大小写正确
- [ ] 变量值不为空
- [ ] 变量值中没有多余的空格
- [ ] 变量值中没有换行符
- [ ] 变量值是完整的 API Key

### 服务检查
- [ ] 已保存环境变量更改
- [ ] 服务已重启
- [ ] 服务状态为 "Live"
- [ ] 日志中没有 token 验证错误

---

## 🎯 快速修复步骤

### 立即执行

**步骤 1**: 重新生成 API Key

1. 访问 https://console.volcengine.com/ark
2. 进入 "API Key 管理"
3. 创建新的 API Key
4. **立即复制并保存**

**步骤 2**: 更新 Render 环境变量

1. 访问 Render 控制台
2. 找到 `COZE_WORKLOAD_IDENTITY_API_KEY`
3. 编辑变量，粘贴新的 API Key
4. 保存

**步骤 3**: 重启服务

1. 点击 "Save Changes"
2. 等待服务重启
3. 等待状态变为 "Live"

**步骤 4**: 测试验证

输入: `你好`

期望: 正常回复

---

## 📞 获取帮助

如果以上方法都无法解决问题：

### 1. 检查火山方舟账号

- ✅ 账号是否正常
- ✅ 是否有足够的权限
- ✅ 是否开通了豆包服务

### 2. 联系火山方舟支持

- 官方文档: https://www.volcengine.com/docs/82379
- 技术支持: 通过火山方舟控制台提交工单

### 3. 提供诊断信息

如果需要帮助，请提供：
- API Key 的前 10 个字符（隐藏敏感信息）
- Render 环境变量配置截图（隐藏敏感信息）
- Render 部署日志
- 完整的错误信息

---

## ✅ 总结

### 问题原因

API Key 验证失败，可能是因为：
- API Key 格式不正确
- API Key 已过期
- 环境变量配置错误

### 解决方案

1. **重新生成并配置 API Key**（推荐）
   - 从火山方舟控制台获取新的 API Key
   - 配置到 Render 环境变量
   - 重启服务

2. **验证 API Key 格式**
   - 确认是 Base64 编码的字符串
   - 确认长度足够
   - 确认没有多余的字符

3. **检查环境变量配置**
   - 确认变量名正确
   - 确认变量值完整
   - 确认没有多余的空格或换行符

### 下一步

1. 访问火山方舟控制台
2. 重新生成 API Key
3. 更新 Render 环境变量
4. 重启服务并测试

---

**现在您可以按照上述步骤重新配置 API Key 了！** 🚀
