# 电商货源猎手智能体 - 功能文档

## 目录
1. [概述](#概述)
2. [核心功能](#核心功能)
3. [工具列表](#工具列表)
4. [数据库集成](#数据库集成)
5. [定期监控](#定期监控)
6. [使用示例](#使用示例)
7. [配置说明](#配置说明)
8. [优化说明](#优化说明)

---

## 概述

电商货源猎手（E-commerce Sourcing Agent）是一个专业的淘宝/拼多多货源寻找助手，通过市场趋势分析、货源搜索和产品潜力评估，为卖家提供高质量、有竞争力的货源推荐。

### 核心价值
- 🎯 **智能选品**：基于市场趋势和数据分析，推荐高潜力货源
- 💰 **精准定价**：自动计算ROI和利润率，优化定价策略
- 📊 **数据驱动**：集成数据库存储，支持历史数据查询和分析
- 🔄 **定期监控**：自动监控市场趋势，及时捕捉商机

---

## 核心功能

### 1. 市场趋势分析
- ✅ 实时获取淘宝/拼多多热搜关键词
- ✅ 分析销量排行和增长率
- ✅ 识别季节性趋势和机会点
- ✅ 生成趋势报告和预测

### 2. 货源搜索与评估
- ✅ 搜索供应商平台（1688、阿里巴巴、义乌市场等）
- ✅ 筛选和过滤供应商（地区、价格、起批量等）
- ✅ 评估供应商信誉和资质
- ✅ 保存供应商信息到数据库

### 3. 产品潜力评估
- ✅ 自动计算ROI和利润率
- ✅ 竞品分析和市场饱和度评估
- ✅ 风险评估（质量、知识产权等）
- ✅ 潜力分数评分系统（1-10分）

### 4. 图片搜索与展示
- ✅ 搜索产品图片参考
- ✅ 支持多图片对比分析
- ✅ 保存图片URL到数据库

### 5. 数据持久化
- ✅ 供应商信息存储
- ✅ 产品信息存储
- ✅ 趋势数据存储
- ✅ 历史查询记录

### 6. 定期趋势监控
- ✅ 自动扫描热门品类
- ✅ 定期更新趋势数据
- ✅ 生成监控报告
- ✅ 支持多平台监控

---

## 工具列表

### 搜索类工具

#### 1. web_search_tool
基础联网搜索，获取实时市场数据。

**参数：**
- `query` (str): 搜索关键词，必填
- `count` (int): 返回结果数量，默认10
- `need_summary` (bool): 是否需要AI摘要，默认True

**示例：**
```python
web_search_tool(query="淘宝面膜热卖趋势", count=10, need_summary=True)
```

---

#### 2. advanced_search_tool
高级搜索，支持站点过滤和时间范围过滤。

**参数：**
- `query` (str): 搜索关键词，必填
- `search_type` (str): 搜索类型 (web/web_summary/image)，默认"web"
- `count` (int): 返回结果数量，默认10
- `sites` (str): 限定搜索的站点，如"taobao.com,1688.com"
- `time_range` (str): 时间范围，如"1d", "1w", "1m"

**示例：**
```python
advanced_search_tool(
    query="面膜批发",
    sites="1688.com",
    time_range="1m",
    count=15
)
```

---

#### 3. image_search_tool
搜索产品图片，提供视觉参考。

**参数：**
- `query` (str): 图片搜索关键词，必填
- `count` (int): 返回图片数量，默认10

**示例：**
```python
image_search_tool(query="面膜产品展示图", count=5)
```

---

### 计算类工具

#### 4. roi_calculator_tool
计算产品的投资回报率(ROI)和利润率。

**参数：**
- `purchase_price` (float): 进货价，必填
- `selling_price` (float): 销售价，必填
- `logistics_cost` (float): 物流费用，默认0
- `quantity` (int): 销售数量，默认1

**返回：**
```json
{
  "purchase_price": 15.0,
  "selling_price": 49.9,
  "logistics_cost": 3.0,
  "quantity": 1,
  "total_cost": 18.0,
  "total_revenue": 49.9,
  "profit": 31.9,
  "profit_margin": 177.22,
  "roi": 177.22,
  "break_even_price": 18.0
}
```

---

### 分析类工具

#### 5. competitor_analysis_tool
分析指定品类在特定平台上的竞争情况。

**参数：**
- `category` (str): 产品品类，必填
- `platform` (str): 目标平台，默认"淘宝"

**示例：**
```python
competitor_analysis_tool(category="面膜", platform="淘宝")
```

---

#### 6. trend_analysis_tool
分析指定品类的市场趋势和热销关键词。

**参数：**
- `category` (str): 产品品类，必填
- `time_range` (str): 时间范围，默认"1m"

**示例：**
```python
trend_analysis_tool(category="面膜", time_range="1m")
```

---

#### 7. supplier_evaluation_tool
评估和推荐供应商，基于品类、地区和价格范围。

**参数：**
- `category` (str): 产品品类，必填
- `region` (str): 地区偏好，可选
- `min_price` (float): 最低进货价，可选
- `max_price` (float): 最高进货价，可选

**示例：**
```python
supplier_evaluation_tool(
    category="面膜",
    region="广州",
    min_price=10,
    max_price=30
)
```

---

### 数据库工具

#### 8. save_supplier_to_db
将供应商信息保存到数据库。

**参数：**
- `name` (str): 供应商名称，必填
- `company_name` (str): 公司名称，可选
- `contact_person` (str): 联系人，可选
- `contact_phone` (str): 联系电话，可选
- `region` (str): 所在地区，可选
- `platform` (str): 主要平台，可选
- `platform_url` (str): 平台店铺URL，可选
- `min_order_quantity` (int): 最小起订量，可选
- `is_verified` (bool): 是否为认证供应商，默认False
- `rating` (float): 评分（0-5分），可选
- `categories` (list): 经营的品类列表，可选
- `tags` (list): 标签列表，可选
- `notes` (str): 备注信息，可选

**示例：**
```python
save_supplier_to_db(
    name="广州XX化妆品有限公司",
    contact_person="张经理",
    contact_phone="138xxxx1234",
    region="广州",
    platform="1688",
    rating=4.8,
    categories=["面膜", "护肤品"],
    tags="实力商家,深度验厂"
)
```

---

#### 9. save_product_to_db
将产品信息保存到数据库。

**参数：**
- `supplier_id` (int): 供应商ID，必填
- `name` (str): 产品名称，必填
- `category` (str): 产品品类，可选
- `purchase_price` (float): 进货价，可选
- `estimated_price` (float): 预估销售价，可选
- `logistics_cost` (float): 物流费用，默认0
- `min_order_quantity` (int): 最小起订量，可选
- `potential_score` (int): 潜力分数（1-10分），可选
- `image_urls` (list): 产品图片URL列表，可选
- `product_url` (str): 产品链接，可选
- `notes` (str): 备注，可选

**示例：**
```python
save_product_to_db(
    supplier_id=1,
    name="玻尿酸补水面膜（10片装）",
    category="面膜",
    purchase_price=18.0,
    estimated_price=49.9,
    logistics_cost=3.0,
    potential_score=9
)
```

---

#### 10. query_suppliers_from_db
从数据库查询供应商信息。

**参数：**
- `category` (str): 产品品类，可选
- `region` (str): 地区，可选
- `platform` (str): 平台，可选
- `min_price` (float): 最低价格，可选
- `max_price` (float): 最高价格，可选
- `limit` (int): 返回数量限制，默认20

**示例：**
```python
query_suppliers_from_db(
    category="面膜",
    region="广州",
    limit=10
)
```

---

#### 11. save_trend_to_db
将市场趋势数据保存到数据库。

**参数：**
- `category` (str): 品类，必填
- `platform` (str): 平台，可选
- `growth_rate` (float): 增长率（%），可选
- `hot_keywords` (list): 热门关键词列表，可选
- `summary` (str): 趋势摘要，可选
- `trend_type` (str): 趋势类型，默认"monthly"

**示例：**
```python
save_trend_to_db(
    category="面膜",
    platform="淘宝",
    growth_rate=85.0,
    hot_keywords=["玻尿酸", "补水", "美白"],
    summary="面膜品类年增长率85%，玻尿酸补水面膜最受欢迎"
)
```

---

#### 12. query_trends_from_db
从数据库查询市场趋势数据。

**参数：**
- `category` (str): 品类，可选
- `platform` (str): 平台，可选
- `limit` (int): 返回数量限制，默认10

**示例：**
```python
query_trends_from_db(category="面膜", platform="淘宝", limit=5)
```

---

## 数据库集成

### 数据表结构

#### 1. suppliers（供应商表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 供应商ID（主键） |
| name | String(255) | 供应商名称 |
| company_name | String(255) | 公司全称 |
| contact_person | String(128) | 联系人 |
| contact_phone | String(50) | 联系电话 |
| region | String(100) | 所在地区 |
| platform | String(50) | 主要平台 |
| is_verified | Boolean | 是否为认证供应商 |
| rating | Float | 评分（0-5分） |
| categories | JSON | 经营的品类列表 |
| tags | JSON | 标签列表 |
| status | String(50) | 状态 |
| created_at | DateTime | 创建时间 |

---

#### 2. products（产品表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 产品ID（主键） |
| supplier_id | Integer | 供应商ID（外键） |
| name | String(255) | 产品名称 |
| category | String(100) | 产品品类 |
| purchase_price | Float | 进货价 |
| estimated_price | Float | 预估销售价 |
| logistics_cost | Float | 物流费用 |
| profit_margin | Float | 利润率（%） |
| roi | Float | 投资回报率（%） |
| potential_score | Integer | 潜力分数（1-10分） |
| image_urls | JSON | 产品图片URL列表 |
| status | String(50) | 状态 |
| created_at | DateTime | 创建时间 |

---

#### 3. market_trends（市场趋势表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 趋势ID（主键） |
| category | String(100) | 品类 |
| platform | String(50) | 平台 |
| trend_data | JSON | 趋势数据 |
| growth_rate | Float | 增长率（%） |
| hot_keywords | JSON | 热门关键词列表 |
| summary | Text | 趋势摘要 |
| trend_type | String(50) | 趋势类型 |
| data_date | DateTime | 数据日期 |
| created_at | DateTime | 创建时间 |

---

### 使用Manager类

```python
from coze_coding_dev_sdk.database import get_session
from storage.database.supplier_manager import (
    SupplierManager, SupplierCreate, ProductCreate
)

# 创建数据库会话
db = get_session()
try:
    mgr = SupplierManager()
    
    # 创建供应商
    supplier_in = SupplierCreate(
        name="广州XX化妆品有限公司",
        region="广州",
        platform="1688",
        rating=4.8
    )
    supplier = mgr.create_supplier(db, supplier_in)
    
    # 创建产品
    product_in = ProductCreate(
        supplier_id=supplier.id,
        name="玻尿酸补水面膜",
        category="面膜",
        purchase_price=18.0,
        estimated_price=49.9
    )
    product = mgr.create_product(db, product_in)
    
    # 查询供应商
    suppliers = mgr.search_suppliers(
        db, category="面膜", region="广州"
    )
    
finally:
    db.close()
```

---

## 定期监控

### 监控脚本

位置：`scripts/trend_monitor.py`

### 功能说明
- ✅ 自动扫描配置的热门品类
- ✅ 支持多平台监控（淘宝、拼多多、京东）
- ✅ 获取实时趋势数据和增长率
- ✅ 保存趋势数据到数据库
- ✅ 生成监控报告

### 使用方法

#### 1. 直接运行
```bash
cd /workspace/projects
python scripts/trend_monitor.py
```

#### 2. 配置监控品类

编辑 `scripts/trend_monitor.py`，修改 `MONITOR_CATEGORIES` 列表：

```python
MONITOR_CATEGORIES = [
    "面膜", "手机壳", "耳机", "护肤品", "电子产品",
    "服装", "美妆", "家居用品", "母婴用品", "运动户外"
]
```

#### 3. 配置监控平台

修改 `MONITOR_PLATFORMS` 列表：

```python
MONITOR_PLATFORMS = ["淘宝", "拼多多", "京东"]
```

#### 4. 设置定时任务（推荐）

使用 cron 或系统定时任务定期执行：

```bash
# 每周一凌晨2点执行
0 2 * * 1 cd /workspace/projects && python scripts/trend_monitor.py
```

### 输出示例

监控报告会保存到 `logs/trend_monitor_YYYYMMDD_HHMMSS.log`

```text
============================================================
电商货源趋势监控报告
============================================================
监控时间: 2025-01-19T10:30:00
成功监控: 25 项
失败监控: 5 项

【成功监控的品类】
  ✓ 面膜 (淘宝) - 增长率: 85.0%
  ✓ 手机壳 (拼多多) - 增长率: 120.0%
  ✓ 耳机 (淘宝) - 增长率: 95.0%

【监控失败的品类】
  ✗ 母婴用品 (淘宝) - 错误: 获取数据失败

============================================================
```

---

## 使用示例

### 示例1：基础货源搜索

**用户输入：**
```
帮我找面膜类的热销货源，预算在50元以内，目标平台是淘宝。
```

**智能体响应：**
1. 使用 `trend_analysis_tool` 分析面膜趋势
2. 使用 `supplier_evaluation_tool` 搜索供应商
3. 使用 `roi_calculator_tool` 计算利润率
4. 生成结构化的推荐列表

---

### 示例2：保存供应商到数据库

**用户输入：**
```
将这个供应商保存到数据库：广州XX化妆品有限公司，联系人张经理，电话138xxxx1234，地区广州，平台1688，评分4.8
```

**智能体响应：**
```
供应商'广州XX化妆品有限公司'已成功保存到数据库，ID: 123
```

---

### 示例3：查询历史供应商

**用户输入：**
```
查询广州地区的面膜供应商
```

**智能体响应：**
1. 使用 `query_suppliers_from_db` 查询数据库
2. 返回符合条件的供应商列表
3. 包含联系方式、评分、经营品类等信息

---

### 示例4：趋势监控

**用户输入：**
```
帮我监控面膜和手机壳的市场趋势
```

**智能体响应：**
1. 使用 `trend_analysis_tool` 获取趋势数据
2. 使用 `save_trend_to_db` 保存到数据库
3. 生成趋势分析报告
4. 提供增长率和热门关键词

---

## 配置说明

### 模型配置

文件：`config/agent_llm_config.json`

```json
{
  "config": {
    "model": "doubao-seed-1-8-251228",
    "temperature": 0.7,
    "top_p": 0.9,
    "max_completion_tokens": 10000,
    "timeout": 600,
    "thinking": "disabled"
  },
  "sp": "System Prompt 内容...",
  "tools": [...]
}
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| model | 使用的模型ID | doubao-seed-1-8-251228 |
| temperature | 输出随机性（0-2） | 0.7 |
| max_completion_tokens | 最大输出token数 | 10000 |
| timeout | 请求超时时间（秒） | 600 |

---

## 优化说明

### 1. System Prompt 优化

**问题：** 智能体未明确何时使用搜索工具，导致工具调用不频繁。

**解决方案：**
- ✅ 明确列出"必须使用工具的场景"
- ✅ 定义工具调用优先级
- ✅ 提供详细的工具使用说明
- ✅ 添加强制调用工具的规则

**效果：** 智能体现在会在需要实时数据时主动调用搜索工具。

---

### 2. 数据库集成

**问题：** 缺少数据持久化，无法保存和查询历史数据。

**解决方案：**
- ✅ 创建 Supplier、Product、MarketTrend 三张表
- ✅ 实现 SupplierManager 管理器类
- ✅ 添加 5 个数据库工具到智能体
- ✅ 支持复杂的查询和过滤

**效果：** 可以保存供应商、产品和趋势数据，支持历史查询和分析。

---

### 3. 图片搜索功能

**问题：** 缺少产品图片参考，无法直观了解产品。

**解决方案：**
- ✅ 添加 `image_search_tool` 工具
- ✅ 支持搜索和展示产品图片
- ✅ 保存图片URL到数据库

**效果：** 可以为用户提供产品图片参考，提升选品体验。

---

### 4. 定期趋势监控

**问题：** 需要手动监控趋势，无法及时发现商机。

**解决方案：**
- ✅ 创建 `trend_monitor.py` 监控脚本
- ✅ 支持配置监控品类和平台
- ✅ 自动保存趋势数据到数据库
- ✅ 生成监控报告

**效果：** 可以定期自动监控市场趋势，及时发现增长机会。

---

### 5. ROI计算自动化

**问题：** 手动计算利润率效率低，容易出错。

**解决方案：**
- ✅ 添加 `roi_calculator_tool` 工具
- ✅ 自动计算利润率、ROI和盈亏平衡点
- ✅ 支持批量计算和比较

**效果：** 快速准确地计算产品盈利能力，辅助决策。

---

## 常见问题

### Q1: 为什么搜索工具没有被调用？

**A:** 请检查 System Prompt 中是否明确了工具调用规则。优化后的 Prompt 已经添加了强制调用工具的规则。如果问题仍然存在，请确认模型配置是否正确。

---

### Q2: 如何添加新的监控品类？

**A:** 编辑 `scripts/trend_monitor.py` 文件，修改 `MONITOR_CATEGORIES` 列表，添加新的品类名称即可。

---

### Q3: 数据库如何备份？

**A:** 可以使用 PostgreSQL 的备份命令：
```bash
pg_dump -h <host> -U <user> -d <database> > backup.sql
```

---

### Q4: 如何提高搜索结果的准确性？

**A:** 
1. 使用更具体的搜索关键词
2. 在 `advanced_search_tool` 中设置 `sites` 参数限定搜索范围
3. 使用 `time_range` 参数获取最新数据

---

### Q5: 监控报告如何查看？

**A:** 监控报告保存在 `logs/` 目录下，文件名格式为 `trend_monitor_YYYYMMDD_HHMMSS.log`。可以直接查看或通过工具查询数据库中的趋势数据。

---

## 更新日志

### v2.0.0 (2025-01-19)
- ✅ 优化 System Prompt，明确工具调用规则
- ✅ 添加数据库集成（供应商、产品、趋势表）
- ✅ 新增 5 个数据库工具
- ✅ 添加图片搜索功能
- ✅ 实现定期趋势监控脚本
- ✅ 优化 ROI 计算工具
- ✅ 修复 Column 对象布尔判断问题

### v1.0.0 (2025-01-18)
- ✅ 初始版本
- ✅ 基础搜索工具（web_search、advanced_search）
- ✅ ROI 计算工具
- ✅ 竞品分析和趋势分析工具
- ✅ 供应商评估工具

---

## 联系支持

如有问题或建议，请联系技术支持团队。

---

**文档版本：** 2.0.0  
**最后更新：** 2025-01-19  
**维护者：** Coze Coding Team
