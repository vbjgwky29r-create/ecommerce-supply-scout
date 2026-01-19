"""
降级服务管理器
当主要服务不可用时，提供本地数据或简化功能
"""
import json
import os
from typing import Any, List, Dict, Optional
from datetime import datetime


class FallbackService:
    """降级服务管理器"""
    
    def __init__(self, fallback_data_dir: str = "assets/fallback_data"):
        """
        初始化降级服务管理器
        
        Args:
            fallback_data_dir: 降级数据存储目录
        """
        self.fallback_data_dir = fallback_data_dir
        self._ensure_data_dir()
    
    def _ensure_data_dir(self) -> None:
        """确保数据目录存在"""
        if not os.path.exists(self.fallback_data_dir):
            os.makedirs(self.fallback_data_dir, exist_ok=True)
    
    def _get_fallback_data_file(self, data_type: str) -> str:
        """
        获取降级数据文件路径
        
        Args:
            data_type: 数据类型
        
        Returns:
            文件路径
        """
        return os.path.join(self.fallback_data_dir, f"{data_type}.json")
    
    def save_fallback_data(self, data_type: str, data: Any) -> None:
        """
        保存降级数据
        
        Args:
            data_type: 数据类型
            data: 数据内容
        """
        file_path = self._get_fallback_data_file(data_type)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump({
                'data': data,
                'updated_at': datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
    
    def load_fallback_data(self, data_type: str) -> Optional[Any]:
        """
        加载降级数据
        
        Args:
            data_type: 数据类型
        
        Returns:
            数据内容，如果不存在则返回 None
        """
        file_path = self._get_fallback_data_file(data_type)
        
        if not os.path.exists(file_path):
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
                return content.get('data')
        except Exception:
            return None
    
    def get_fallback_search_results(self, keyword: str, platform: str = "通用") -> Dict:
        """
        获取降级搜索结果
        
        Args:
            keyword: 搜索关键词
            platform: 平台
        
        Returns:
            降级搜索结果
        """
        fallback_data = self.load_fallback_data(f"search_{platform}")
        
        # 如果没有降级数据，返回通用数据
        if not fallback_data:
            return {
                "platform": platform,
                "keyword": keyword,
                "total_results": 0,
                "message": "当前搜索服务限流，请稍后重试。系统已记录您的搜索需求，服务恢复后会自动搜索。",
                "fallback_mode": True
            }
        
        # 如果有降级数据，返回缓存的结果
        return {
            "platform": platform,
            "keyword": keyword,
            "total_results": len(fallback_data) if isinstance(fallback_data, list) else 0,
            "results": fallback_data if isinstance(fallback_data, list) else [fallback_data],
            "message": "当前搜索服务限流，返回缓存的历史搜索结果。",
            "fallback_mode": True
        }
    
    def get_fallback_trend_data(self, category: str, days: int = 30) -> Dict:
        """
        获取降级趋势数据
        
        Args:
            category: 品类
            days: 天数
        
        Returns:
            降级趋势数据
        """
        fallback_data = self.load_fallback_data(f"trend_{category}")
        
        if not fallback_data:
            return {
                "category": category,
                "days": days,
                "message": "当前趋势分析服务限流，无法获取实时数据。建议您稍后重试。",
                "fallback_mode": True
            }
        
        return {
            "category": category,
            "days": days,
            "avg_growth_rate": fallback_data.get("avg_growth_rate", 0),
            "max_growth_rate": fallback_data.get("max_growth_rate", 0),
            "min_growth_rate": fallback_data.get("min_growth_rate", 0),
            "message": "当前趋势分析服务限流，返回缓存的历史趋势数据。",
            "fallback_mode": True
        }
    
    def get_fallback_suppliers(self, category: str = None, region: str = None,
                               platform: str = None, limit: int = 10) -> Dict:
        """
        获取降级供应商数据
        
        Args:
            category: 品类
            region: 地区
            platform: 平台
            limit: 数量限制
        
        Returns:
            降级供应商数据
        """
        fallback_data = self.load_fallback_data("suppliers")
        
        if not fallback_data:
            return {
                "total": 0,
                "suppliers": [],
                "message": "当前数据库服务限流，无法查询供应商数据。建议您稍后重试。",
                "fallback_mode": True
            }
        
        suppliers = fallback_data if isinstance(fallback_data, list) else []
        
        # 简单过滤
        filtered = []
        for sup in suppliers:
            match = True
            if category and category not in sup.get('categories', []):
                match = False
            if region and sup.get('region') != region:
                match = False
            if platform and sup.get('platform') != platform:
                match = False
            if match:
                filtered.append(sup)
        
        return {
            "total": len(filtered),
            "suppliers": filtered[:limit],
            "message": "当前数据库服务限流，返回缓存的供应商数据。",
            "fallback_mode": True
        }


# 全局降级服务实例
_fallback_service = None

def get_fallback_service() -> FallbackService:
    """获取全局降级服务实例"""
    global _fallback_service
    if _fallback_service is None:
        _fallback_service = FallbackService()
    return _fallback_service


def save_search_result_cache(keyword: str, platform: str, results: List) -> None:
    """
    保存搜索结果到降级缓存
    
    Args:
        keyword: 搜索关键词
        platform: 平台
        results: 搜索结果
    """
    fallback = get_fallback_service()
    fallback.save_fallback_data(f"search_{platform}", {
        "keyword": keyword,
        "results": results[:20],  # 只保存前20条
        "cached_at": datetime.now().isoformat()
    })


def save_trend_data_cache(category: str, trend_data: Dict) -> None:
    """
    保存趋势数据到降级缓存
    
    Args:
        category: 品类
        trend_data: 趋势数据
    """
    fallback = get_fallback_service()
    fallback.save_fallback_data(f"trend_{category}", {
        "category": category,
        "trend_data": trend_data,
        "cached_at": datetime.now().isoformat()
    })
