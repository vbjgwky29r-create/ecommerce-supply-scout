# 服务限流问题解决方案

## 问题说明
当前数据分析服务（数据库、搜索等）可能处于限流状态，导致无法获取实时数据。

## 解决方案

### 1. 缓存机制（已实现）

**原理**：缓存常用的查询结果，减少重复请求。

**优势**：
- 减少对服务的调用次数
- 提升响应速度
- 自动管理缓存过期时间

**使用方式**：
```python
from utils.cache_manager import get_cache_manager

cache = get_cache_manager()

# 保存到缓存
cache.set("search_key", data, ttl=1800)  # 缓存30分钟

# 从缓存读取
data = cache.get("search_key")
```

### 2. 限流保护（已实现）

**原理**：控制请求频率，避免触发限流。

**优势**：
- 自动计算合适的请求间隔
- 防止短时间内大量请求
- 支持可配置的限流策略

**使用方式**：
```python
from utils.rate_limiter import check_service_available, handle_service_error

# 检查服务是否可用
if check_service_available("search"):
    # 执行搜索
    pass
else:
    # 服务不可用，使用降级数据
    pass

# 标记服务不可用
handle_service_error("search", cooldown=300)  # 5分钟后重试
```

### 3. 降级服务（已实现）

**原理**：当主要服务不可用时，使用本地缓存数据。

**优势**：
- 确保服务始终可用
- 提供基本功能支持
- 自动切换，用户无感知

**使用方式**：
```python
from utils.fallback_service import get_fallback_service

fallback = get_fallback_service()

# 获取降级搜索结果
result = fallback.get_fallback_search_results(keyword="面膜")

# 获取降级趋势数据
trend = fallback.get_fallback_trend_data(category="面膜")
```

### 4. 重试机制（已实现）

**原理**：自动重试失败的请求，带指数退避。

**优势**：
- 自动处理临时错误
- 避免立即重试导致的进一步限流
- 可配置重试次数和延迟

**使用方式**：
```python
from utils.rate_limiter import retry_with_backoff

@retry_with_backoff(max_retries=3, base_delay=1.0)
def search_with_retry():
    # 搜索逻辑
    pass
```

## 实际使用建议

### 对用户

1. **等待服务恢复**：限流通常是临时的，等待几分钟后重试
2. **使用缓存数据**：系统会自动返回缓存的历史数据
3. **批量操作分批进行**：避免一次性查询大量数据
4. **优先使用本地数据**：如果已有数据，优先查询本地数据库

### 对开发者

1. **使用增强版工具**：
   - `web_search_tool_with_cache`：带缓存的搜索工具
   - `batch_search_with_rate_limit`：带限流的批量搜索
   - `get_service_status`：查看服务状态

2. **优化查询策略**：
   - 避免短时间内重复查询相同内容
   - 批量操作时添加延迟
   - 优先使用缓存数据

3. **监控服务状态**：
   - 定期检查服务可用性
   - 记录限流时间和频率
   - 根据实际情况调整限流参数

## 配置文件

位置：`config/rate_limit_config.json`

```json
{
  "rate_limit": {
    "max_calls_per_minute": 30,
    "max_calls_per_hour": 300,
    "cooldown_time": 300
  },
  "cache": {
    "default_ttl": 3600,
    "search_ttl": 1800,
    "trend_ttl": 3600,
    "supplier_ttl": 7200
  },
  "retry": {
    "max_retries": 3,
    "base_delay": 1.0,
    "max_delay": 10.0,
    "backoff_factor": 2.0
  }
}
```

## 故障排查步骤

1. **检查服务状态**
   ```
   调用 get_service_status 工具
   ```

2. **清空缓存**
   ```python
   from utils.cache_manager import get_cache_manager
   cache = get_cache_manager()
   cache.clear()
   ```

3. **重置服务状态**
   ```python
   from utils.rate_limiter import get_service_availability
   availability = get_service_availability()
   availability.service_status.clear()
   ```

4. **查看降级数据**
   ```bash
   ls assets/fallback_data/
   ```

## 常见问题

### Q1: 为什么总是提示限流？
A: 可能是短时间内请求过于频繁。建议：
- 使用缓存数据
- 增加请求间隔
- 分批处理任务

### Q2: 降级数据多久更新一次？
A: 降级数据在服务正常时会自动更新。缓存过期时间默认为30分钟到2小时，可在配置文件中调整。

### Q3: 如何判断服务是否恢复？
A: 调用 `get_service_status` 工具，查看各服务的 `available` 状态。

### Q4: 批量导入数据时如何避免限流？
A: 使用 `batch_search_with_rate_limit` 工具，会自动在请求之间添加延迟。

## 总结

通过缓存、限流、降级和重试四重保护机制，系统可以在服务限流时仍提供基本服务。建议：
1. 优先使用带缓存和降级的增强版工具
2. 监控服务状态，合理安排任务
3. 批量操作时分批进行，避免集中请求

如遇持续限流问题，请联系技术支持团队。
