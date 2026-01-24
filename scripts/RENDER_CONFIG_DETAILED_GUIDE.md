# Render 环境变量配置 - 超详细操作指南

## 📋 目录
1. [访问 Render 控制台](#步骤-1-访问-render-控制台)
2. [查看所有环境变量](#步骤-2-查看所有环境变量)
3. [搜索和定位特定变量](#步骤-3-搜索和定位特定变量)
4. [删除 OpenAI 相关的变量](#步骤-4删除-openai-相关的变量)
5. [添加豆包相关的变量](#步骤-5添加豆包相关的变量)
6. [保存和重启](#步骤-6保存和重启)
7. [验证配置](#步骤-7验证配置)
8. [常见问题](#常见问题)

---

## 步骤 1: 访问 Render 控制台

### 1.1 打开浏览器
- 使用 Chrome、Firefox 或 Edge 浏览器

### 1.2 登录 Render
1. 访问网址：**https://dashboard.render.com/**
2. 如果未登录，点击右上角的 **"Log In"**
3. 使用您的账号登录（GitHub、GitLab、Email 或 Google）

### 1.3 找到您的服务
1. 在左侧导航栏，找到您的项目名称
2. 点击展开项目
3. 找到您的服务（通常显示为 **Web Service**）
4. 点击服务名称进入服务详情页

### 1.4 进入环境变量页面
1. 在服务详情页顶部，找到标签页：
   - Overview
   - **Environment** ← 点击这个
   - Events
   - Logs
   - Metrics
   - Settings

2. 点击 **"Environment"** 标签

---

## 步骤 2: 查看所有环境变量

### 2.1 找到环境变量区域
在 Environment 页面，您会看到：
- **Environment Variables** 区域
- 可能有一些已经配置的变量
- 每个变量都有一个 **Key**（变量名）和 **Value**（变量值）

### 2.2 展开所有变量
如果您看不到全部变量：

#### 方法 1: 滚动页面
- 向下滚动页面
- 环境变量列表可能会很长

#### 方法 2: 查看分页
- 查看页面底部是否有 **"Load More"** 或 **"Show More"** 按钮
- 点击以加载更多变量

#### 方法 3: 使用搜索功能（推荐）
- 在环境变量区域上方，可能有一个搜索框
- 输入关键词进行搜索

---

## 步骤 3: 搜索和定位特定变量

### 3.1 搜索 OpenAI 相关的变量

#### 如果有搜索框：
1. 在搜索框中输入：`openai`（小写）
2. 按回车或点击搜索按钮
3. 查看搜索结果

#### 如果没有搜索框：
1. 在键盘上按 `Ctrl + F`（Windows）或 `Cmd + F`（Mac）
2. 在弹出的搜索框中输入：`openai`（小写）
3. 按回车或点击搜索
4. 浏览器会高亮显示所有匹配项

### 3.2 查找可能的关键词

搜索以下关键词，确保没有遗漏：
- `openai`
- `OPENAI`
- `anthropic`
- `ANTHROPIC`
- `azure`
- `AZURE`

### 3.3 搜索豆包相关的变量

搜索以下关键词，确认是否已配置：
- `COZE_WORKLOAD_IDENTITY_API_KEY`
- `COZE_INTEGRATION_MODEL_BASE_URL`
- `COZE_WORKSPACE_PATH`

---

## 步骤 4: 删除 OpenAI 相关的变量

### 4.1 找到需要删除的变量

根据搜索结果，找到以下变量（如果存在）：
- ❌ `OPENAI_API_KEY`
- ❌ `OPENAI_ORGANIZATION`
- ❌ `OPENAI_BASE_URL`
- ❌ `OPENAI_API_VERSION`
- ❌ 任何其他包含 `openai` 或 `OPENAI` 的变量

### 4.2 删除变量的方法

#### 方法 1: 使用删除按钮（推荐）
1. 找到要删除的变量
2. 在该变量的右侧，找到 **"×"** 或 **"Delete"** 按钮
3. 点击删除按钮
4. 确认删除（如果弹出确认对话框）

#### 方法 2: 使用编辑功能
1. 找到要删除的变量
2. 点击该变量的 **"Edit"** 或 **"Modify"** 按钮
3. 删除变量名和变量值
4. 点击 **"Cancel"** 或关闭编辑窗口
5. 然后使用删除按钮删除该变量

### 4.3 批量删除

如果需要删除多个变量：
1. 逐个找到每个变量
2. 逐个删除
3. 确保所有 OpenAI 相关的变量都被删除

**注意**：Render 可能不支持批量删除，需要逐个删除。

### 4.4 验证删除

删除完成后，再次搜索 `openai`，确保：
- ✅ 没有任何 OpenAI 相关的变量
- ✅ 页面显示 "No results" 或没有高亮

---

## 步骤 5: 添加豆包相关的变量

### 5.1 找到添加变量的位置

在 Environment 页面，找到：
- **"Add Environment Variable"** 按钮
- 或 **"New Environment Variable"** 链接
- 或一个空的输入框（Key 和 Value）

### 5.2 添加第一个变量：COZE_WORKLOAD_IDENTITY_API_KEY

1. 点击 **"Add Environment Variable"**
2. 在 **Key** 输入框中输入：
   ```
   COZE_WORKLOAD_IDENTITY_API_KEY
   ```
   （**注意**：大写字母，用下划线连接，不要有空格）

3. 在 **Value** 输入框中输入您的火山方舟 API Key

   **如何获取 API Key**：
   - 访问：https://console.volcengine.com/ark
   - 登录您的账号
   - 进入 "API Key 管理"
   - 创建新的 API Key
   - 复制 API Key

4. 在 **Type** 下拉框中，选择：
   - **Secret**（推荐，隐藏 API Key）
   - 或 **Sensitive**（如果有的话）

5. 点击 **"Add"** 或 **"Save"** 按钮

### 5.3 添加第二个变量：COZE_INTEGRATION_MODEL_BASE_URL

1. 再次点击 **"Add Environment Variable"**
2. 在 **Key** 输入框中输入：
   ```
   COZE_INTEGRATION_MODEL_BASE_URL
   ```

3. 在 **Value** 输入框中输入：
   ```
   https://integration.coze.cn/api/v3
   ```

4. 在 **Type** 下拉框中，选择：
   - **Plain Text**（这不是敏感信息）

5. 点击 **"Add"** 或 **"Save"** 按钮

### 5.4 添加第三个变量：COZE_WORKSPACE_PATH

1. 再次点击 **"Add Environment Variable"**
2. 在 **Key** 输入框中输入：
   ```
   COZE_WORKSPACE_PATH
   ```

3. 在 **Value** 输入框中输入：
   ```
   /app
   ```

4. 在 **Type** 下拉框中，选择：
   - **Plain Text**（这不是敏感信息）

5. 点击 **"Add"** 或 **"Save"** 按钮

### 5.5 验证添加

添加完成后，确认：
- ✅ `COZE_WORKLOAD_IDENTITY_API_KEY` 已添加
- ✅ `COZE_INTEGRATION_MODEL_BASE_URL` 已添加
- ✅ `COZE_WORKSPACE_PATH` 已添加
- ✅ 所有变量的值都正确

---

## 步骤 6: 保存和重启

### 6.1 保存更改

1. 在页面底部或顶部，找到 **"Save Changes"** 按钮
2. 点击 **"Save Changes"**
3. 等待保存完成（通常几秒钟）

### 6.2 自动重启服务

保存环境变量后，Render 会：
1. 显示提示：**"Restarting service..."**
2. 自动停止当前服务
3. 使用新的环境变量重新部署

### 6.3 等待重启完成

1. 在页面顶部，查看服务状态：
   - **Deploying** → 正在部署
   - **Live** → 部署完成

2. 点击 **"Events"** 标签查看部署进度
3. 点击 **"Logs"** 标签查看详细日志

**预计时间**：2-5 分钟

### 6.4 确认服务状态

当状态变为 **"Live"** 时，表示：
- ✅ 服务已成功启动
- ✅ 新的环境变量已生效
- ✅ 应用已准备好使用

---

## 步骤 7: 验证配置

### 7.1 访问应用

1. 在服务详情页，找到 **"Domain"** 或 **"URL"**
2. 点击 URL 打开应用
3. 等待页面加载

### 7.2 测试智能体

在应用的聊天界面中，输入：
```
你好
```

#### 期望结果：
```
您好！我是**陈艳红专用电商猎手**，同时是资深的**纺织品专家**...
```

#### 如果仍然报错：

如果仍然显示 OpenAI API key 错误：
1. 返回 Environment 页面
2. 重新检查环境变量
3. 确保没有遗漏任何 OpenAI 相关的变量
4. 确保豆包相关的变量都已正确配置

### 7.3 查看日志（可选）

如果仍有问题，查看详细日志：

1. 点击 **"Logs"** 标签
2. 查看最新的日志输出
3. 搜索关键词：
   - `Error`
   - `API key`
   - `401`
   - `Exception`

### 7.4 运行诊断脚本（可选）

如果 Render 支持在服务器上运行脚本，可以执行：

```bash
cd /app
python scripts/diagnose_environment.py
```

---

## 常见问题

### Q1: 我看不到 "Environment" 标签

**A**: 请确保：
1. 您已经登录 Render
2. 您点击了正确的服务
3. 您有足够的权限（Admin 或 Owner）

### Q2: 我找不到 "Add Environment Variable" 按钮

**A**: 可能的位置：
1. 在环境变量列表的底部
2. 在页面右上角
3. 在一个 "Settings" 区域内

### Q3: 我不确定是否删除了所有 OpenAI 相关的变量

**A**:
1. 在键盘上按 `Ctrl + F`（Windows）或 `Cmd + F`（Mac）
2. 搜索 `openai`（小写）
3. 确保没有任何匹配项

### Q4: 我不知道我的火山方舟 API Key

**A**: 按以下步骤获取：
1. 访问：https://console.volcengine.com/ark
2. 登录您的账号
3. 进入 "API Key 管理"
4. 创建新的 API Key
5. 复制 API Key

**注意**：API Key 只显示一次，请立即复制保存！

### Q5: 我添加了环境变量，但服务重启失败

**A**: 可能的原因：
1. API Key 格式不正确
2. API Key 已过期
3. 网络连接问题

**解决方案**：
1. 检查 API Key 是否完整复制
2. 重新生成新的 API Key
3. 查看详细日志，定位具体错误

### Q6: 页面显示不全，我看不到所有环境变量

**A**: 尝试：
1. 使用浏览器的全屏模式（按 `F11`）
2. 使用搜索功能（Ctrl + F 或 Cmd + F）
3. 查看页面是否有 "Load More" 按钮

### Q7: 我不确定变量名的大小写

**A**: 变量名区分大小写，必须完全匹配：

✅ **正确**：
```
COZE_WORKLOAD_IDENTITY_API_KEY
COZE_INTEGRATION_MODEL_BASE_URL
COZE_WORKSPACE_PATH
```

❌ **错误**：
```
coze_workload_identity_api_key (全部小写)
Coze_Workload_Identity_Api_Key (大小写混合)
COZE_WORKLOAD_IDENTITY_APIkey (拼写错误)
```

### Q8: 我添加了变量，但 Value 显示为空

**A**: 检查：
1. 您是否输入了 Value
2. 您是否点击了 "Add" 或 "Save" 按钮
3. 如果是 Secret 类型，Value 可能被隐藏，这是正常的

---

## 快速检查清单

完成配置后，请确认：

### 删除操作
- [ ] 已搜索并删除所有 OpenAI 相关的变量
- [ ] 已确认没有任何 `openai` 或 `OPENAI` 的变量
- [ ] 已删除 `OPENAI_API_KEY`（如果存在）
- [ ] 已删除 `OPENAI_ORGANIZATION`（如果存在）
- [ ] 已删除 `OPENAI_BASE_URL`（如果存在）

### 添加操作
- [ ] 已添加 `COZE_WORKLOAD_IDENTITY_API_KEY`
- [ ] 已添加 `COZE_INTEGRATION_MODEL_BASE_URL`
- [ ] 已添加 `COZE_WORKSPACE_PATH`
- [ ] 所有变量名的大小写都正确
- [ ] 所有变量的值都正确

### 保存和重启
- [ ] 已点击 "Save Changes"
- [ ] 服务已自动重启
- [ ] 服务状态为 "Live"

### 验证测试
- [ ] 可以访问应用
- [ ] 输入 "你好" 后正常回复
- [ ] 不显示 OpenAI API key 错误
- [ ] 智能体可以正常对话

---

## 🎯 关键提醒

### ⚠️ 重要提示

1. **本应用使用豆包大模型，不是 OpenAI**
   - API Key 必须是火山方舟的
   - API 地址是 `https://integration.coze.cn/api/v3`

2. **变量名必须完全匹配**
   - 大小写敏感
   - 不要有空格
   - 不要有拼写错误

3. **API Key 只显示一次**
   - 创建后立即复制保存
   - 不要泄露给他人

4. **保存后必须等待服务重启**
   - 不要立即测试
   - 等待状态变为 "Live"

5. **如果不确定，使用搜索功能**
   - Ctrl + F 或 Cmd + F
   - 搜索关键词快速定位

---

## 📞 需要帮助？

如果按照本指南操作后仍有问题，请提供：
1. Render 环境变量列表的截图（隐藏敏感信息）
2. Render 部署日志
3. 完整的错误信息
4. 您的操作步骤

---

**祝您配置顺利！** 🚀
