# Render 环境变量配置指南

## 问题诊断

您遇到的错误信息：
```
❌ 处理失败: Error code: 401 - {'error': {'message': 'Incorrect API key provided: e863036f************************65c8. You can find your API key at https://platform.openai.com/account/api-keys.', 'type': 'invalid_request_error', 'param': None, 'code': 'invalid_api_key'}}
```

这个错误显示的是 **OpenAI API key 错误**，但我们的应用使用的是**豆包大模型**，不需要 OpenAI API key。

## 正确的环境变量配置

### 必需的环境变量

请确保在 Render 上配置了以下环境变量：

1. **COZE_WORKLOAD_IDENTITY_API_KEY**
   - 类型: Secret
   - 值: 火山方舟 API Key（不是 OpenAI API Key！）
   - 说明: 这是豆包大模型的 API Key

2. **COZE_INTEGRATION_MODEL_BASE_URL**
   - 类型: Plain Text
   - 值: `https://integration.coze.cn/api/v3`
   - 说明: 这是豆包大模型的 API 地址

3. **COZE_WORKSPACE_PATH**
   - 类型: Plain Text
   - 值: `/app` (或 `/workspace/projects`)
   - 说明: 应用的工作目录

### 错误的配置

❌ **不要配置以下环境变量**：
- `OPENAI_API_KEY` - 本应用不使用 OpenAI
- `ANTHROPIC_API_KEY` - 本应用不使用 Anthropic
- `AZURE_OPENAI_API_KEY` - 本应用不使用 Azure OpenAI

如果您配置了这些变量，请删除它们。

## 如何检查和修复 Render 环境变量

### 步骤 1: 访问 Render 控制台

1. 登录 [Render](https://dashboard.render.com/)
2. 找到您的服务
3. 点击 "Environment" 标签

### 步骤 2: 检查环境变量

查看现有的环境变量，确认：

✅ **必须有的变量**：
- `COZE_WORKLOAD_IDENTITY_API_KEY`
- `COZE_INTEGRATION_MODEL_BASE_URL`

❌ **不应该有的变量**：
- `OPENAI_API_KEY`
- 任何其他 OpenAI 相关的变量

### 步骤 3: 修复配置

#### 如果缺少必需的变量：

添加以下环境变量：

```
COZE_WORKLOAD_IDENTITY_API_KEY=<您的火山方舟 API Key>
COZE_INTEGRATION_MODEL_BASE_URL=https://integration.coze.cn/api/v3
COZE_WORKSPACE_PATH=/app
```

#### 如果有错误的变量：

删除所有 OpenAI 相关的变量：
- `OPENAI_API_KEY`
- `OPENAI_ORGANIZATION`
- `OPENAI_BASE_URL`

### 步骤 4: 保存并重启服务

1. 点击 "Save Changes"
2. Render 会自动重启服务
3. 等待服务重启完成（约 2-3 分钟）

### 步骤 5: 验证配置

服务重启后，访问应用并测试：

```
输入: 你好
期望: 正常回复，不显示 API key 错误
```

## 如何获取火山方舟 API Key

如果您还没有火山方舟 API Key，请按以下步骤获取：

1. 访问 [火山方舟控制台](https://console.volcengine.com/ark)
2. 登录您的账号
3. 进入 "API Key 管理"
4. 创建新的 API Key
5. 复制 API Key 并保存

## 验证脚本

如果您需要在 Render 上运行诊断脚本，可以执行：

```bash
python scripts/diagnose_environment.py
```

这会检查所有必需的环境变量和配置。

## 常见问题

### Q1: 错误信息提到 OpenAI，但我配置的是豆包

**A**: 这可能是因为：
1. 环境变量中配置了 OpenAI API Key（错误的配置）
2. 某个工具或客户端尝试使用 OpenAI 格式调用

**解决方案**:
1. 检查 Render 环境变量，删除所有 OpenAI 相关的变量
2. 确保只配置了豆包相关的环境变量

### Q2: 我不确定 API Key 是否正确

**A**: 您可以通过以下方式验证：

1. 检查 API Key 的格式：
   - 火山方舟 API Key 通常是 Base64 编码的字符串
   - 开头不是 "sk-"（OpenAI 的格式）

2. 使用诊断脚本：
   ```bash
   python scripts/diagnose_environment.py
   ```

### Q3: 修改环境变量后仍然报错

**A**: 请尝试：
1. 确保修改后点击了 "Save Changes"
2. 等待 Render 服务重启完成
3. 检查 Render 的部署日志，查看是否有其他错误
4. 清除浏览器缓存，重新访问应用

### Q4: 如何查看 Render 部署日志

**A**:
1. 访问 Render 控制台
2. 找到您的服务
3. 点击 "Logs" 标签
4. 查看最新的日志输出

## 联系支持

如果以上方法都无法解决问题，请提供以下信息：

1. Render 环境变量配置（隐藏敏感信息）
2. Render 部署日志
3. 完整的错误信息
4. 运行诊断脚本的输出

## 快速检查清单

- [ ] 已删除所有 OpenAI 相关的环境变量
- [ ] 已配置 `COZE_WORKLOAD_IDENTITY_API_KEY`
- [ ] 已配置 `COZE_INTEGRATION_MODEL_BASE_URL`
- [ ] 已配置 `COZE_WORKSPACE_PATH`
- [ ] 已保存环境变量更改
- [ ] 已重启 Render 服务
- [ ] 服务成功启动
- [ ] 可以正常与智能体对话

---

**注意**: 本应用使用的是火山方舟（豆包）大模型，不需要 OpenAI API Key。请确保环境变量配置正确。
