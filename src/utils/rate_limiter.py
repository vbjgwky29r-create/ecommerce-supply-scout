"""
请求限流和重试机制
用于防止 API 限流和处理临时错误
"""
import time
import random
from typing import Callable, Any, Optional
from functools import wraps


class RateLimiter:
    """请求限流器"""
    
    def __init__(self, max_calls: int = 10, time_window: int = 60):
        """
        初始化限流器
        
        Args:
            max_calls: 时间窗口内最大调用次数
            time_window: 时间窗口（秒）
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
    
    def can_make_call(self) -> bool:
        """
        检查是否可以进行调用
        
        Returns:
            是否可以调用
        """
        now = time.time()
        
        # 清除过期记录
        self.calls = [call_time for call_time in self.calls if now - call_time < self.time_window]
        
        return len(self.calls) < self.max_calls
    
    def record_call(self) -> None:
        """记录一次调用"""
        self.calls.append(time.time())
    
    def wait_time(self) -> float:
        """
        获取需要等待的时间
        
        Returns:
            需要等待的秒数，如果可以立即调用则返回 0
        """
        if self.can_make_call():
            return 0.0
        
        now = time.time()
        oldest_call = self.calls[0]
        return oldest_call + self.time_window - now


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 10.0,
    backoff_factor: float = 2.0,
    jitter: bool = True
) -> Callable:
    """
    带指数退避的重试装饰器
    
    Args:
        max_retries: 最大重试次数
        base_delay: 基础延迟（秒）
        max_delay: 最大延迟（秒）
        backoff_factor: 退避因子
        jitter: 是否添加随机抖动
    
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    # 如果是最后一次尝试，直接抛出异常
                    if attempt == max_retries:
                        break
                    
                    # 计算延迟时间
                    delay = min(base_delay * (backoff_factor ** attempt), max_delay)
                    
                    # 添加随机抖动
                    if jitter:
                        delay *= random.uniform(0.5, 1.5)
                    
                    # 等待
                    time.sleep(delay)
            
            # 所有重试都失败，抛出最后的异常
            raise last_exception
        
        return wrapper
    return decorator


class ServiceAvailability:
    """服务可用性管理器"""
    
    def __init__(self):
        """初始化服务可用性管理器"""
        self.service_status = {}  # 服务名称 -> {available: bool, last_checked: timestamp}
    
    def mark_available(self, service_name: str) -> None:
        """
        标记服务可用
        
        Args:
            service_name: 服务名称
        """
        self.service_status[service_name] = {
            'available': True,
            'last_checked': time.time()
        }
    
    def mark_unavailable(self, service_name: str, cooldown: int = 300) -> None:
        """
        标记服务不可用
        
        Args:
            service_name: 服务名称
            cooldown: 冷却时间（秒），默认5分钟
        """
        self.service_status[service_name] = {
            'available': False,
            'last_checked': time.time(),
            'cooldown_until': time.time() + cooldown
        }
    
    def is_available(self, service_name: str) -> bool:
        """
        检查服务是否可用
        
        Args:
            service_name: 服务名称
        
        Returns:
            是否可用
        """
        if service_name not in self.service_status:
            return True  # 未知服务，假设可用
        
        status = self.service_status[service_name]
        
        # 检查冷却期是否已过
        if not status['available'] and time.time() > status.get('cooldown_until', 0):
            # 冷却期已过，重置为可用
            status['available'] = True
        
        return status['available']
    
    def get_status(self, service_name: str) -> dict:
        """
        获取服务状态
        
        Args:
            service_name: 服务名称
        
        Returns:
            服务状态字典
        """
        if service_name not in self.service_status:
            return {'available': True, 'status': 'unknown'}
        
        status = self.service_status[service_name]
        return {
            'available': status['available'],
            'last_checked': status.get('last_checked'),
            'cooldown_until': status.get('cooldown_until')
        }


# 全局服务可用性管理器实例
_service_availability = None

def get_service_availability() -> ServiceAvailability:
    """获取全局服务可用性管理器实例"""
    global _service_availability
    if _service_availability is None:
        _service_availability = ServiceAvailability()
    return _service_availability


def handle_service_error(service_name: str, cooldown: int = 300) -> None:
    """
    处理服务错误，标记服务不可用
    
    Args:
        service_name: 服务名称
        cooldown: 冷却时间（秒）
    """
    availability = get_service_availability()
    availability.mark_unavailable(service_name, cooldown)


def check_service_available(service_name: str) -> bool:
    """
    检查服务是否可用
    
    Args:
        service_name: 服务名称
    
    Returns:
        是否可用
    """
    availability = get_service_availability()
    return availability.is_available(service_name)
