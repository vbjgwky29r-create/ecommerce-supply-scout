"""
增强版工具示例
展示如何使用缓存、限流和降级机制来应对服务限流
"""
import json
from langchain.tools import tool, ToolRuntime
from coze_coding_utils.runtime_ctx.context import new_context
from coze_coding_dev_sdk import SearchClient, get_session
from utils.cache_manager import get_cache_manager, cache_key
from utils.rate_limiter import check_service_available, handle_service_error, retry_with_backoff
from utils.fallback_service import get_fallback_service, save_search_result_cache


@tool
def web_search_tool_with_cache(query: str, count: int = 10, need_summary: bool = True) -> str:
    """
    执行联网搜索，带缓存和降级支持。
    当服务限流时，自动使用缓存数据或降级服务。
    
    Args:
        query: 搜索关键词
        count: 返回结果数量
        need_summary: 是否需要AI摘要
    
    Returns:
        搜索结果
    """
    # 检查缓存
    cache = get_cache_manager()
    cache_key_str = cache_key("web_search", query=query, count=count)
    
    cached_result = cache.get(cache_key_str)
    if cached_result:
        result_data = json.loads(cached_result)
        result_data["from_cache"] = True
        result_data["message"] = "从缓存返回数据（服务可能限流，使用缓存避免重复请求）"
        return json.dumps(result_data, ensure_ascii=False, indent=2)
    
    # 检查服务可用性
    if not check_service_available("search"):
        # 服务不可用，使用降级数据
        fallback = get_fallback_service()
        fallback_result = fallback.get_fallback_search_results(query, "通用")
        return json.dumps(fallback_result, ensure_ascii=False, indent=2)
    
    try:
        # 执行搜索
        ctx = new_context(method="search.web")
        client = SearchClient(ctx=ctx)
        
        response = client.web_search(
            query=query,
            count=count,
            need_summary=need_summary
        )
        
        results = []
        if response.web_items:
            for item in response.web_items:
                result = {
                    "title": item.title,
                    "url": item.url,
                    "snippet": item.snippet,
                    "site_name": item.site_name,
                    "summary": item.summary if hasattr(item, 'summary') else "",
                    "publish_time": item.publish_time if hasattr(item, 'publish_time') else ""
                }
                results.append(result)
        
        output = {
            "query": query,
            "total_results": len(results),
            "ai_summary": response.summary if hasattr(response, 'summary') else "",
            "results": results,
            "from_cache": False
        }
        
        # 保存到缓存（30分钟）
        cache.set(cache_key_str, json.dumps(output, ensure_ascii=False), ttl=1800)
        
        # 保存到降级数据
        save_search_result_cache(query, "通用", results)
        
        return json.dumps(output, ensure_ascii=False, indent=2)
        
    except Exception as e:
        # 服务错误，标记服务不可用
        handle_service_error("search", cooldown=300)
        
        # 使用降级数据
        fallback = get_fallback_service()
        fallback_result = fallback.get_fallback_search_results(query, "通用")
        fallback_result["error"] = str(e)
        return json.dumps(fallback_result, ensure_ascii=False, indent=2)


@tool
def batch_search_with_rate_limit(queries: list, delay: float = 2.0) -> str:
    """
    批量搜索，带限流保护。
    在多个搜索之间自动添加延迟，避免触发限流。
    
    Args:
        queries: 搜索关键词列表
        delay: 搜索之间的延迟（秒）
    
    Returns:
        批量搜索结果
    """
    import time
    
    results = []
    cache = get_cache_manager()
    
    for idx, query in enumerate(queries):
        # 检查缓存
        cache_key_str = cache_key("web_search", query=query, count=5)
        cached_result = cache.get(cache_key_str)
        
        if cached_result:
            result_data = json.loads(cached_result)
            result_data["from_cache"] = True
            result_data["query_index"] = idx
            results.append(result_data)
            continue
        
        # 不是第一个查询，添加延迟
        if idx > 0:
            time.sleep(delay)
        
        try:
            ctx = new_context(method="search.batch")
            client = SearchClient(ctx=ctx)
            
            response = client.web_search(
                query=query,
                count=5,
                need_summary=True
            )
            
            search_results = []
            if response.web_items:
                for item in response.web_items:
                    search_results.append({
                        "title": item.title,
                        "url": item.url,
                        "snippet": item.snippet,
                        "site_name": item.site_name
                    })
            
            result = {
                "query": query,
                "query_index": idx,
                "total_results": len(search_results),
                "results": search_results,
                "from_cache": False
            }
            
            # 保存到缓存
            cache.set(cache_key_str, json.dumps(result, ensure_ascii=False), ttl=1800)
            
            results.append(result)
            
        except Exception as e:
            results.append({
                "query": query,
                "query_index": idx,
                "error": str(e),
                "from_cache": False
            })
    
    output = {
        "total_queries": len(queries),
        "successful": len([r for r in results if "error" not in r]),
        "from_cache": len([r for r in results if r.get("from_cache")]),
        "results": results
    }
    
    return json.dumps(output, ensure_ascii=False, indent=2)


@tool
def get_service_status() -> str:
    """
    获取各服务的当前状态。
    
    Returns:
        服务状态信息
    """
    from utils.rate_limiter import get_service_availability
    from utils.cache_manager import get_cache_manager
    from utils.fallback_service import get_fallback_service
    
    availability = get_service_availability()
    cache = get_cache_manager()
    fallback = get_fallback_service()
    
    services = ["search", "database", "trend"]
    
    status_info = {
        "timestamp": "当前时间",
        "services": {},
        "cache_stats": cache.get_stats(),
        "fallback_data_dir": fallback.fallback_data_dir
    }
    
    for service in services:
        is_available = availability.is_available(service)
        status = availability.get_status(service)
        
        status_info["services"][service] = {
            "available": is_available,
            "status": "可用" if is_available else "限流/不可用",
            "last_checked": status.get("last_checked", "未知")
        }
    
    return json.dumps(status_info, ensure_ascii=False, indent=2)
