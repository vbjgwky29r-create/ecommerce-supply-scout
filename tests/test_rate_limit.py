"""
测试限流保护机制
"""
import json
import time
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.cache_manager import get_cache_manager
from src.utils.rate_limiter import RateLimiter, check_service_available, handle_service_error
from src.utils.fallback_service import get_fallback_service


def test_cache_manager():
    """测试缓存管理器"""
    print("\n=== 测试缓存管理器 ===")
    
    cache = get_cache_manager()
    
    # 测试设置和获取
    cache.set("test_key", {"data": "test_value"}, ttl=60)
    result = cache.get("test_key")
    print(f"✓ 缓存设置和获取: {result}")
    
    # 测试统计
    stats = cache.get_stats()
    print(f"✓ 缓存统计: {stats}")
    
    # 测试删除
    cache.delete("test_key")
    result = cache.get("test_key")
    print(f"✓ 缓存删除后: {result}")
    
    print("缓存管理器测试通过！")


def test_rate_limiter():
    """测试限流器"""
    print("\n=== 测试限流器 ===")
    
    limiter = RateLimiter(max_calls=5, time_window=10)
    
    # 测试调用记录
    for i in range(5):
        assert limiter.can_make_call(), f"第{i+1}次调用应该允许"
        limiter.record_call()
        print(f"✓ 第{i+1}次调用记录成功")
    
    # 测试限流
    assert not limiter.can_make_call(), "应该触发限流"
    print("✓ 限流触发成功")
    
    # 测试等待时间
    wait_time = limiter.wait_time()
    print(f"✓ 需要等待时间: {wait_time:.2f}秒")
    
    print("限流器测试通过！")


def test_service_availability():
    """测试服务可用性管理"""
    print("\n=== 测试服务可用性管理 ===")
    
    # 测试初始状态
    assert check_service_available("test_service"), "初始状态应该可用"
    print("✓ 服务初始可用")
    
    # 测试标记不可用
    handle_service_error("test_service", cooldown=60)
    assert not check_service_available("test_service"), "应该标记为不可用"
    print("✓ 服务标记为不可用")
    
    print("服务可用性管理测试通过！")


def test_fallback_service():
    """测试降级服务"""
    print("\n=== 测试降级服务 ===")
    
    fallback = get_fallback_service()
    
    # 测试保存和加载数据
    test_data = {"keyword": "面膜", "results": [{"title": "测试结果"}]}
    fallback.save_fallback_data("search_test", test_data)
    
    loaded_data = fallback.load_fallback_data("search_test")
    assert loaded_data == test_data, "保存和加载的数据应该一致"
    print("✓ 降级数据保存和加载成功")
    
    # 测试获取降级搜索结果
    result = fallback.get_fallback_search_results("面膜", "1688")
    print(f"✓ 降级搜索结果: {len(result.get('results', []))}条")
    
    # 测试获取降级趋势数据
    trend = fallback.get_fallback_trend_data("面膜")
    print(f"✓ 降级趋势数据: {trend.get('category')}")
    
    print("降级服务测试通过！")


def test_batch_operations():
    """测试批量操作"""
    print("\n=== 测试批量操作 ===")
    
    limiter = RateLimiter(max_calls=3, time_window=10)
    cache = get_cache_manager()
    
    queries = ["面膜", "护肤品", "彩妆", "香水", "口红"]
    
    results = []
    for idx, query in enumerate(queries):
        # 检查限流
        if not limiter.can_make_call():
            wait_time = limiter.wait_time()
            print(f"⏳ 等待 {wait_time:.2f} 秒后继续...")
            time.sleep(wait_time + 0.1)
        
        # 检查缓存
        cache_key = f"search_{query}"
        cached = cache.get(cache_key)
        
        if cached:
            results.append({"query": query, "from_cache": True})
            print(f"✓ 第{idx+1}个查询从缓存获取: {query}")
        else:
            # 模拟搜索
            results.append({"query": query, "from_cache": False})
            cache.set(cache_key, f"result_{query}", ttl=60)
            limiter.record_call()
            print(f"✓ 第{idx+1}个查询执行搜索: {query}")
    
    print(f"✓ 批量操作完成: {len(results)}个查询，{len([r for r in results if r['from_cache']])}个来自缓存")
    
    print("批量操作测试通过！")


def run_all_tests():
    """运行所有测试"""
    print("=" * 50)
    print("开始测试限流保护机制")
    print("=" * 50)
    
    try:
        test_cache_manager()
        test_rate_limiter()
        test_service_availability()
        test_fallback_service()
        test_batch_operations()
        
        print("\n" + "=" * 50)
        print("✓ 所有测试通过！")
        print("=" * 50)
        
    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}")
    except Exception as e:
        print(f"\n✗ 测试出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
