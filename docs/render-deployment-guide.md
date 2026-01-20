# 🚀 电商货源猎手 - Render 部署指南

本指南将帮助您将电商货源猎手智能体部署到 Render 平台，完全免费！

---

## 📋 前置准备

- ✅ GitHub 仓库：`https://github.com/vbjgwky29r-create/ecommerce-supply-scout.git`
- ✅ API Key：`e863036f-fe71-4771-9510-9a5d329d65c8`
- ✅ 项目代码已推送到 GitHub

---

## ⏱️ 预计完成时间：5-10 分钟

---

## 🎯 步骤 1：注册并登录 Render

### 1.1 访问 Render

打开浏览器，访问：https://render.com/

### 1.2 创建账户

1. 点击右上角的 **"Get Started"** 按钮
2. 选择 **"Sign up with GitHub"**
3. 授权 Render 访问您的 GitHub 账号
4. 按照提示完成注册（免费）

**注意**：Render 使用 GitHub 账号登录，无需单独注册。

---

## 🎯 步骤 2：创建新的 Web Service

### 2.1 进入创建页面

登录后：

1. 在 Render 仪表板（Dashboard）
2. 点击右上角的 **"+ New"** 按钮
3. 在下拉菜单中选择 **"Web Service"**

---

## 🎯 步骤 3：连接 GitHub 仓库

### 3.1 连接 GitHub

1. 在 **"Build and deploy from a Git repository"** 部分
2. 点击 **"Connect GitHub"** 按钮
3. 在弹出窗口中，授权 Render 访问您的 GitHub 账号
4. 点击 **"Authorize render-inc"** 按钮

### 3.2 选择仓库

1. 在搜索框中输入：`ecommerce-supply-scout`
2. 选择您的仓库：`vbigwky29r-create/ecommerce-supply-scout`
3. 点击 **"Connect"** 按钮

---

## 🎯 步骤 4：配置部署设置

### 4.1 基本信息

在 **"Name & Region"** 部分：

- **Name**: `ecommerce-scout`（或您喜欢的名字）
- **Region**: 选择 **"Singapore"**（亚洲区域，速度更快）
- **Branch**: 确认是 `main` 分支

### 4.2 运行时配置

在 **"Runtime"** 部分：

- **Environment**: 选择 **"Python 3"**

### 4.3 构建配置

在 **"Build & Deploy"** 部分：

- **Build Command**:
  ```
  pip install -r requirements.txt
  ```

- **Start Command**:
  ```
  python src/web/app.py
  ```

**重要提示**：
- Start Command 必须是 `python src/web/app.py`（从项目根目录启动）
- 不要使用 `cd src/web`，因为 Render 会从根目录执行

---

## 🎯 步骤 5：配置环境变量

### 5.1 打开环境变量设置

在页面底部找到 **"Environment"** 部分，点击 **"Advanced"** 展开更多选项。

### 5.2 添加环境变量

点击 **"Add Environment Variable"**，依次添加以下变量：

#### 变量 1：FLASK_SECRET_KEY

- **Key**: `FLASK_SECRET_KEY`
- **Value**: `ecommerce-agent-secret-key-2024`
- 点击 **"Add"**

#### 变量 2：COZE_WORKLOAD_IDENTITY_API_KEY

- **Key**: `COZE_WORKLOAD_IDENTITY_API_KEY`
- **Value**: `e863036f-fe71-4771-9510-9a5d329d65c8`
- 点击 **"Add"**

#### 变量 3：PORT（重要！）

- **Key**: `PORT`
- **Value**: `5000`
- 点击 **"Add"**

**为什么需要 PORT？**
Render 会自动分配一个端口号，应用需要监听这个端口。

---

## 🎯 步骤 6：创建 Web Service

### 6.1 确认所有配置

检查以下配置是否正确：

- ✅ Name: `ecommerce-scout`
- ✅ Region: `Singapore`（或其他您选择的区域）
- ✅ Branch: `main`
- ✅ Runtime: `Python 3`
- ✅ Build Command: `pip install -r requirements.txt`
- ✅ Start Command: `python src/web/app.py`
- ✅ 3个环境变量已添加

### 6.2 创建服务

1. 滚动到页面底部
2. 确认定价计划是 **"Free"**（免费）
3. 点击 **"Create Web Service"** 按钮

---

## 🎯 步骤 7：等待部署完成

### 7.1 查看部署进度

1. 进入部署页面后，会自动开始部署
2. 您可以看到实时日志输出
3. 部署过程包括：
   - Cloning repository（克隆代码）
   - Installing dependencies（安装依赖）
   - Starting service（启动服务）

### 7.2 等待时间

- **预计时间**: 3-5 分钟
- 首次部署可能稍慢，因为需要安装所有依赖

### 7.3 部署状态

- ⏳ **In Progress**: 正在部署
- ✅ **Live**: 部署成功
- ❌ **Failed**: 部署失败（查看日志排查问题）

---

## 🎯 步骤 8：获取访问链接

### 8.1 查看应用 URL

部署成功后：

1. 在项目页面顶部，会显示一个 URL
2. 格式类似：`https://ecommerce-scout.onrender.com`
3. 或者：`https://ecommerce-scout-xxxx.onrender.com`

### 8.2 测试访问

1. 点击 URL 打开应用
2. 应该能看到电商货源猎手的界面
3. 可以尝试发送消息测试功能

### 8.3 分享给朋友

1. 复制应用 URL
2. 在微信中发送给朋友
3. 朋友点击链接即可在微信浏览器中使用

---

## 🎨 分享文案示例

```
我找到了一个超好用的电商货源猎手智能体！🛒

✅ 可以搜索热卖商品货源
✅ 分析市场趋势和竞争情况
✅ 上传图片自动识别产品
✅ 计算利润和投资回报率

试试看：https://ecommerce-scout.onrender.com

#电商 #货源 #AI智能体 #创业
```

---

## 🔧 故障排除

### 问题 1：部署失败

**可能原因**：
- Start Command 错误
- 依赖安装失败
- 端口配置错误

**解决方案**：
1. 检查 Start Command 是否是 `python src/web/app.py`
2. 查看部署日志，找到具体错误信息
3. 确认 `PORT` 环境变量已设置为 `5000`

### 问题 2：应用无法访问

**可能原因**：
- 应用还在启动中
- 端口监听错误

**解决方案**：
1. 等待 1-2 分钟，让应用完全启动
2. 检查 Logs 标签，查看是否有错误
3. 确认代码中使用了 `os.getenv('PORT', 5000)` 监听端口

### 问题 3：应用响应慢

**可能原因**：
- Render 免费版有冷启动时间
- 依赖安装时间长

**解决方案**：
1. 首次访问可能需要 30-60 秒冷启动
2. 定期访问可以保持应用活跃
3. 考虑升级到付费计划（如果需要更好性能）

### 问题 4：环境变量无效

**可能原因**：
- 变量名拼写错误
- 变量值不正确

**解决方案**：
1. 检查环境变量名称是否完全匹配（大小写敏感）
2. 确认 API Key 格式正确
3. 重新部署应用（修改环境变量后需要重新部署）

---

## 📊 Render 免费额度说明

### 免费计划特点

- ✅ **750 小时/月**（约 31 天全天候运行）
- ✅ **512 MB RAM**
- ✅ **0.1 CPU**
- ✅ **自动 HTTPS**
- ✅ **自动重试失败部署**

### 注意事项

1. **冷启动**：免费版应用在 15 分钟无访问后会休眠，重新访问需要 30-60 秒冷启动
2. **内存限制**：如果应用内存超过 512 MB，会被杀死
3. **重启频率**：如果应用频繁重启，可能需要优化代码或升级计划

---

## 🔄 如何更新应用

### 修改代码后重新部署

1. 在本地修改代码
2. 提交到 GitHub：
   ```bash
   git add .
   git commit -m "update: 描述您的修改"
   git push
   ```
3. Render 会自动检测到更新并重新部署

### 手动触发部署

1. 进入 Render 项目页面
2. 点击 **"Manual Deploy"**
3. 选择 **"Clear build cache & deploy"**（清除缓存重新部署）

---

## 💡 优化建议

### 1. 加快冷启动速度

- 减少不必要的依赖
- 使用轻量级的数据库连接池
- 延迟加载非必需模块

### 2. 降低内存使用

- 使用生成器替代列表
- 及时释放不再使用的对象
- 限制对话历史长度（已实现）

### 3. 提高稳定性

- 添加错误处理和日志记录
- 实现健康检查端点
- 配置自动重试机制

---

## 🎉 完成！

恭喜您完成部署！现在您可以：

✅ 随时随地通过公网链接访问智能体  
✅ 在微信中分享给朋友使用  
✅ 享受 Render 免费额度（750 小时/月）

---

## 📞 技术支持

### 获取帮助

- 查看 Render 文档：https://render.com/docs
- 查看 Render 状态：https://status.render.com
- 查看 GitHub 仓库：https://github.com/vbjgwky29r-create/ecommerce-supply-scout

### 查看日志

1. 进入 Render 项目页面
2. 点击 **"Logs"** 标签
3. 查看实时日志输出

---

## 🎯 总结

### 部署流程回顾

1. ✅ 注册并登录 Render
2. ✅ 创建 Web Service
3. ✅ 连接 GitHub 仓库
4. ✅ 配置部署设置
5. ✅ 添加环境变量
6. ✅ 创建并等待部署
7. ✅ 获取访问链接

### 关键配置

- **Start Command**: `python src/web/app.py`
- **环境变量**: 3个（FLASK_SECRET_KEY, API_KEY, PORT）
- **端口**: 5000

---

**祝您部署顺利，使用愉快！** 🚀
