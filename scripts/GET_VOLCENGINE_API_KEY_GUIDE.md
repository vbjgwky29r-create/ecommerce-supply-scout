# 如何获取正确的火山方舟 API Key

## 🚨 问题确认

您提供的 `b32eafb1-8ddd-49a5-a836-7518382d8f37` 是 **UUID 格式**，不是火山方舟的 API Key。

**正确的火山方舟 API Key 格式**：
- 32位加密字符串（Base64 编码）
- 长度通常 100+ 字符
- 不包含连字符
- 示例：`aHJkd25NSmhSWENDQzdnZ1JhVnJ0b2ZwdHRtYnI0eGJxNnN2cH...`

---

## 📖 获取正确 API Key 的步骤

### 步骤 1: 登录火山方舟控制台

1. 访问：https://console.volcengine.com/ark
2. 登录您的火山引擎账号

### 步骤 2: 进入 API Key 管理

1. 在左侧导航栏，找到 **"API Key 管理"**
2. 点击进入

### 步骤 3: 创建新的 API Key

1. 点击 **"创建 API Key"** 按钮
2. 设置名称（可选）
3. 选择权限范围（通常选择 **"全部权限"**）
4. 点击 **"确定"**

### 步骤 4: 复制 API Key

**⚠️ 重要**：API Key **只显示一次**，请立即复制并保存！

**正确格式示例**：
```
aHJkd25NSmhSWENDQzdnZ1JhVnJ0b2ZwdHRtYnI0eGJxNnN2cH...
```

**特征**：
- Base64 编码的字符串
- 长度 100+ 字符
- 不包含连字符
- 只包含字母、数字和 `+`、`/`、`=` 等字符

---

## 🔄 更新 Render 环境变量

### 步骤 1: 访问 Render 控制台

1. 访问：https://dashboard.render.com/
2. 找到您的服务
3. 点击 "Environment" 标签

### 步骤 2: 编辑 API Key 变量

1. 找到 `COZE_WORKLOAD_IDENTITY_API_KEY` 变量
2. 点击编辑按钮
3. 删除旧的值（UUID 格式的）
4. 粘贴新的 API Key（Base64 格式的）
5. 点击保存

**注意事项**：
- ✅ 直接粘贴，不要添加引号
- ✅ 不要添加空格或换行符
- ✅ 确保是完整的 API Key（不要截断）

### 步骤 3: 重启服务

1. 点击 "Save Changes"
2. 等待服务自动重启（2-5 分钟）
3. 等待状态变为 "Live"

### 步骤 4: 测试验证

1. 访问应用 URL
2. 输入: `你好`
3. 确认正常回复

---

## 📋 API Key 格式对比

### ❌ 错误格式（您提供的）

```
b32eafb1-8ddd-49a5-a836-7518382d8f37
```

**特征**：
- UUID 格式
- 36 字符
- 包含 4 个连字符
- 这可能是 Service ID 或其他标识符

### ✅ 正确格式（火山方舟 API Key）

```
aHJkd25NSmhSWENDQzdnZ1JhVnJ0b2ZwdHRtYnI0eGJxNnN2cH...
```

**特征**：
- Base64 编码的字符串
- 长度 100+ 字符
- 不包含连字符
- 只包含字母、数字和 `+`、`/`、`=` 等字符

---

## 🔍 验证 API Key

### 本地测试

创建测试脚本 `test_api_key.py`：

```python
import os
from langchain_openai import ChatOpenAI

# 获取 API Key
api_key = "YOUR_API_KEY_HERE"  # 替换为您的 API Key
base_url = "https://integration.coze.cn/api/v3"

print(f"API Key: {api_key[:20]}...")
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

## ⚠️ 常见错误

### 错误 1: 使用 UUID 格式的字符串

**错误**：
```
b32eafb1-8ddd-49a5-a836-7518382d8f37
```

**原因**：这可能是 Service ID 或其他标识符，不是 API Key。

**解决**：从 API Key 管理页面重新创建 API Key。

### 错误 2: API Key 不完整

**错误**：
```
aHJkd25NSmhSWENDQzdn...
```

**原因**：只复制了部分内容。

**解决**：确保复制完整的 API Key。

### 错误 3: API Key 包含引号或空格

**错误**：
```
"aHJkd25NSmhSWENDQzdn..."
aHJkd25NSmhSWENDQzdn... 
```

**原因**：粘贴时添加了引号或空格。

**解决**：直接粘贴，不要添加任何字符。

---

## 📞 需要帮助？

如果按照上述步骤操作后仍有问题：

1. **检查火山方舟账号**
   - ✅ 账号是否正常
   - ✅ 是否有足够的权限
   - ✅ 是否开通了豆包服务

2. **联系火山方舟支持**
   - 官方文档: https://www.volcengine.com/docs/82379
   - 技术支持: 通过火山方舟控制台提交工单

3. **提供诊断信息**
   - API Key 的前 10 个字符（隐藏敏感信息）
   - Render 环境变量配置截图（隐藏敏感信息）
   - Render 部署日志
   - 完整的错误信息

---

## ✅ 总结

### 问题

您提供的 `b32eafb1-8ddd-49a5-a836-7518382d8f37` 是 UUID 格式，不是火山方舟的 API Key。

### 解决方案

1. 访问 https://console.volcengine.com/ark
2. 进入 API Key 管理
3. 创建新的 API Key（32位加密字符串，Base64 格式）
4. 立即复制并保存（只显示一次）
5. 更新 Render 环境变量
6. 重启服务并测试

### 关键点

- ✅ 火山方舟 API Key 是 Base64 编码的字符串
- ✅ 长度通常 100+ 字符
- ✅ 不包含连字符
- ✅ 只显示一次，需要立即复制保存

---

**现在请按照上述步骤获取正确的 API Key！** 🚀
