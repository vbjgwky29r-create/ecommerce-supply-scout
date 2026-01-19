#!/usr/bin/env python3
"""
定期趋势监控脚本
用于定期扫描热门品类的市场趋势，并将结果保存到数据库
"""
import sys
import os
import json
import logging
from datetime import datetime
from typing import List, Dict

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from coze_coding_dev_sdk import SearchClient, get_session
from coze_coding_utils.runtime_ctx.context import new_context
from storage.database.supplier_manager import SupplierManager, MarketTrendCreate

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# 待监控的热门品类列表
MONITOR_CATEGORIES = [
    "面膜", "手机壳", "耳机", "护肤品", "电子产品",
    "服装", "美妆", "家居用品", "母婴用品", "运动户外"
]

# 监控平台
MONITOR_PLATFORMS = ["淘宝", "拼多多", "京东"]


def fetch_market_trend(category: str, platform: str = "淘宝") -> Dict:
    """
    获取指定品类在指定平台的市场趋势数据
    
    Args:
        category: 品类名称
        platform: 平台名称
    
    Returns:
        趋势数据字典
    """
    try:
        ctx = new_context(method="trend.monitor")
        client = SearchClient(ctx=ctx)
        
        # 搜索趋势关键词
        search_query = f"{platform} {category} 热销趋势 增长率 2025"
        
        response = client.web_search(
            query=search_query,
            count=10,
            need_summary=True
        )
        
        trend_data = {
            "category": category,
            "platform": platform,
            "summary": response.summary if hasattr(response, 'summary') else "",
            "results": []
        }
        
        # 提取搜索结果
        if response.web_items:
            for item in response.web_items:
                result = {
                    "title": item.title,
                    "url": item.url,
                    "snippet": item.snippet,
                    "site_name": item.site_name
                }
                trend_data["results"].append(result)
        
        # 尝试从摘要中提取增长率
        growth_rate = None
        if response.summary:
            import re
            # 查找百分比数字
            match = re.search(r'(\d+\.?\d*)%?', response.summary)
            if match:
                growth_rate = float(match.group(1))
        
        trend_data["growth_rate"] = growth_rate
        
        logger.info(f"成功获取品类 '{category}' 在 '{platform}' 的趋势数据")
        return trend_data
        
    except Exception as e:
        logger.error(f"获取趋势数据失败: {category} - {platform}, 错误: {str(e)}")
        return None


def save_trend_to_database(trend_data: Dict, db_session) -> bool:
    """
    将趋势数据保存到数据库
    
    Args:
        trend_data: 趋势数据字典
        db_session: 数据库会话
    
    Returns:
        是否保存成功
    """
    try:
        mgr = SupplierManager()
        
        # 提取热门关键词
        hot_keywords = []
        for result in trend_data.get("results", []):
            if result.get("title"):
                # 简单的关键词提取
                keywords = result["title"].split()
                hot_keywords.extend(keywords[:3])
        
        # 去重并限制数量
        hot_keywords = list(set(hot_keywords))[:10]
        
        trend_in = MarketTrendCreate(
            category=trend_data["category"],
            platform=trend_data["platform"],
            growth_rate=trend_data.get("growth_rate"),
            hot_keywords=hot_keywords,
            summary=trend_data.get("summary", ""),
            trend_type="monthly",
            data_date=datetime.now()
        )
        
        trend = mgr.create_market_trend(db_session, trend_in)
        logger.info(f"趋势数据已保存到数据库: ID={trend.id}")
        return True
        
    except Exception as e:
        logger.error(f"保存趋势数据到数据库失败: {str(e)}")
        return False


def monitor_all_categories() -> Dict[str, List[Dict]]:
    """
    监控所有配置的品类和平台
    
    Returns:
        监控结果字典
    """
    results = {
        "success": [],
        "failed": [],
        "timestamp": datetime.now().isoformat()
    }
    
    db = get_session()
    try:
        for category in MONITOR_CATEGORIES:
            for platform in MONITOR_PLATFORMS:
                logger.info(f"正在监控: {category} - {platform}")
                
                # 获取趋势数据
                trend_data = fetch_market_trend(category, platform)
                
                if trend_data:
                    # 保存到数据库
                    if save_trend_to_database(trend_data, db):
                        results["success"].append({
                            "category": category,
                            "platform": platform,
                            "growth_rate": trend_data.get("growth_rate")
                        })
                    else:
                        results["failed"].append({
                            "category": category,
                            "platform": platform,
                            "error": "保存失败"
                        })
                else:
                    results["failed"].append({
                        "category": category,
                        "platform": platform,
                        "error": "获取数据失败"
                    })
        
        # 提交数据库事务
        db.commit()
        
    except Exception as e:
        logger.error(f"监控过程出错: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()
    
    return results


def generate_monitoring_report(results: Dict) -> str:
    """
    生成监控报告
    
    Args:
        results: 监控结果字典
    
    Returns:
        报告文本
    """
    report = []
    report.append("=" * 60)
    report.append("电商货源趋势监控报告")
    report.append("=" * 60)
    report.append(f"监控时间: {results['timestamp']}")
    report.append(f"成功监控: {len(results['success'])} 项")
    report.append(f"失败监控: {len(results['failed'])} 项")
    report.append("")
    
    if results["success"]:
        report.append("【成功监控的品类】")
        for item in results["success"]:
            report.append(f"  ✓ {item['category']} ({item['platform']}) - "
                         f"增长率: {item['growth_rate'] or '未知'}%")
        report.append("")
    
    if results["failed"]:
        report.append("【监控失败的品类】")
        for item in results["failed"]:
            report.append(f"  ✗ {item['category']} ({item['platform']}) - "
                         f"错误: {item['error']}")
        report.append("")
    
    report.append("=" * 60)
    
    return "\n".join(report)


def main():
    """主函数"""
    logger.info("开始执行趋势监控任务")
    
    try:
        # 执行监控
        results = monitor_all_categories()
        
        # 生成报告
        report = generate_monitoring_report(results)
        logger.info("\n" + report)
        
        # 保存报告到文件
        report_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "logs",
            f"trend_monitor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )
        
        # 确保日志目录存在
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"监控报告已保存到: {report_path}")
        
        # 输出JSON结果（用于程序化处理）
        json_output = {
            "status": "completed",
            "success_count": len(results["success"]),
            "failed_count": len(results["failed"]),
            "results": results
        }
        
        print(json.dumps(json_output, ensure_ascii=False, indent=2))
        
    except Exception as e:
        logger.error(f"监控任务执行失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
