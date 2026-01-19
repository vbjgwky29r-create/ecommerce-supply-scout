"""
缓存管理器
用于减少重复的数据库查询和搜索请求
"""
import time
import json
from typing import Any, Optional
from datetime import datetime, timedelta


class CacheManager:
    """简单的内存缓存管理器"""
    
    def __init__(self, default_ttl: int = 3600):
        """
        初始化缓存管理器
        
        Args:
            default_ttl: 默认缓存过期时间（秒），默认1小时
        """
        self.cache = {}
        self.default_ttl = default_ttl
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值
        
        Args:
            key: 缓存键
        
        Returns:
            缓存值，如果不存在或已过期则返回 None
        """
        if key not in self.cache:
            return None
        
        item = self.cache[key]
        
        # 检查是否过期
        if item['expires_at'] < datetime.now():
            del self.cache[key]
            return None
        
        return item['value']
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒），如果为 None 则使用默认值
        """
        if ttl is None:
            ttl = self.default_ttl
        
        expires_at = datetime.now() + timedelta(seconds=ttl)
        
        self.cache[key] = {
            'value': value,
            'expires_at': expires_at,
            'created_at': datetime.now()
        }
    
    def delete(self, key: str) -> bool:
        """
        删除缓存值
        
        Args:
            key: 缓存键
        
        Returns:
            是否删除成功
        """
        if key in self.cache:
            del self.cache[key]
            return True
        return False
    
    def clear(self) -> None:
        """清空所有缓存"""
        self.cache.clear()
    
    def get_stats(self) -> dict:
        """
        获取缓存统计信息
        
        Returns:
            统计信息字典
        """
        now = datetime.now()
        active_count = sum(1 for item in self.cache.values() if item['expires_at'] >= now)
        expired_count = len(self.cache) - active_count
        
        return {
            'total_keys': len(self.cache),
            'active_keys': active_count,
            'expired_keys': expired_count
        }


# 全局缓存管理器实例
_cache_manager = None

def get_cache_manager() -> CacheManager:
    """获取全局缓存管理器实例"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


def cache_key(prefix: str, **kwargs) -> str:
    """
    生成缓存键
    
    Args:
        prefix: 键前缀
        **kwargs: 键参数
    
    Returns:
        缓存键字符串
    """
    # 对参数进行排序，确保相同的参数生成相同的键
    sorted_params = sorted(kwargs.items())
    params_str = "&".join([f"{k}={v}" for k, v in sorted_params])
    return f"{prefix}:{params_str}"
