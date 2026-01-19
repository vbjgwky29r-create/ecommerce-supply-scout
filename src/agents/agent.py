import os
import json
from typing import Annotated
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage
from langchain.tools import tool, ToolRuntime
from coze_coding_utils.runtime_ctx.context import default_headers, new_context
from coze_coding_dev_sdk import SearchClient, get_session
from storage.memory.memory_saver import get_memory_saver
from storage.database.db import execute_with_retry
from storage.database.supplier_manager import (
    SupplierManager, SupplierCreate, ProductCreate, 
    ProductUpdate, MarketTrendCreate
)
from storage.database.shared.model import Supplier, Product, MarketTrend, UserPreference, Notification

LLM_CONFIG = "config/agent_llm_config.json"

# 默认保留最近 20 轮对话 (40 条消息)
MAX_MESSAGES = 40

def _windowed_messages(old, new):
    """滑动窗口: 只保留最近 MAX_MESSAGES 条消息"""
    return add_messages(old, new)[-MAX_MESSAGES:]  # type: ignore

class AgentState(MessagesState):
    messages: Annotated[list[AnyMessage], _windowed_messages]

@tool
def web_search_tool(query: str, count: int = 10, need_summary: bool = True) -> str:
    """
    执行联网搜索，获取实时市场数据、供应商信息和产品趋势。
    
    Args:
        query: 搜索关键词，如"淘宝面膜热卖趋势"、"1688手机壳批发"等
        count: 返回结果数量，默认10条
        need_summary: 是否需要AI生成的摘要，默认True
    
    Returns:
        搜索结果的JSON格式字符串，包含标题、URL、摘要、AI总结等信息
    """
    try:
        # 使用new_context创建context
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
            "results": results
        }
        
        return json.dumps(output, ensure_ascii=False, indent=2)
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return f"搜索失败: {str(e)}\n详细信息: {error_details}"

@tool
def advanced_search_tool(query: str, search_type: str = "web", count: int = 10,
                         sites: str = None, time_range: str = None) -> str:
    """
    执行高级联网搜索，支持站点过滤和时间范围过滤。
    
    Args:
        query: 搜索关键词
        search_type: 搜索类型 (web/web_summary/image)
        count: 返回结果数量
        sites: 限定搜索的站点，如"taobao.com,1688.com"
        time_range: 时间范围，如"1d"(1天), "1w"(1周), "1m"(1个月)
    
    Returns:
        搜索结果的JSON格式字符串
    """
    try:
        ctx = new_context(method="search.advanced")
        client = SearchClient(ctx=ctx)
        
        response = client.search(
            query=query,
            search_type=search_type,
            count=count,
            sites=sites,
            time_range=time_range,
            need_summary=(search_type == "web_summary")
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
            "search_type": search_type,
            "total_results": len(results),
            "ai_summary": response.summary if hasattr(response, 'summary') else "",
            "results": results
        }
        
        return json.dumps(output, ensure_ascii=False, indent=2)
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return f"高级搜索失败: {str(e)}\n详细信息: {error_details}"

@tool
def image_search_tool(query: str, count: int = 10) -> str:
    """
    搜索产品图片，用于视觉参考和市场分析。
    
    Args:
        query: 图片搜索关键词，如"面膜产品图"、"手机壳设计"等
        count: 返回图片数量，默认10张
    
    Returns:
        图片搜索结果的JSON格式字符串，包含图片URL、尺寸、来源等信息
    """
    try:
        ctx = new_context(method="search.image")
        client = SearchClient(ctx=ctx)
        
        response = client.image_search(
            query=query,
            count=count
        )
        
        images = []
        if response.image_items:
            for item in response.image_items:
                image_info = {
                    "title": item.title,
                    "url": item.url,
                    "site_name": item.site_name,
                    "image_url": item.image.url if hasattr(item.image, 'url') else "",
                    "width": item.image.width if hasattr(item.image, 'width') else 0,
                    "height": item.image.height if hasattr(item.image, 'height') else 0,
                    "shape": item.image.shape if hasattr(item.image, 'shape') else ""
                }
                images.append(image_info)
        
        output = {
            "query": query,
            "total_images": len(images),
            "images": images
        }
        
        return json.dumps(output, ensure_ascii=False, indent=2)
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return f"图片搜索失败: {str(e)}\n详细信息: {error_details}"

@tool
def roi_calculator_tool(purchase_price: float, selling_price: float, logistics_cost: float = 0, 
                        quantity: int = 1) -> str:
    """
    计算产品的投资回报率(ROI)和利润率。
    
    Args:
        purchase_price: 进货价（元）
        selling_price: 销售价（元）
        logistics_cost: 物流费用（元），默认0
        quantity: 销售数量，默认1
    
    Returns:
        ROI计算结果的JSON格式字符串
    """
    try:
        # 计算总成本
        total_cost = purchase_price * quantity + logistics_cost
        
        # 计算总收入
        total_revenue = selling_price * quantity
        
        # 计算利润
        profit = total_revenue - total_cost
        
        # 计算利润率
        profit_margin = (profit / total_cost) * 100 if total_cost > 0 else 0
        
        # 计算ROI
        roi = (profit / total_cost) * 100 if total_cost > 0 else 0
        
        # 计算盈亏平衡点
        break_even_price = (total_cost / quantity) if quantity > 0 else purchase_price
        
        output = {
            "purchase_price": purchase_price,
            "selling_price": selling_price,
            "logistics_cost": logistics_cost,
            "quantity": quantity,
            "total_cost": total_cost,
            "total_revenue": total_revenue,
            "profit": profit,
            "profit_margin": round(profit_margin, 2),
            "roi": round(roi, 2),
            "break_even_price": round(break_even_price, 2)
        }
        
        return json.dumps(output, ensure_ascii=False, indent=2)
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return f"ROI计算失败: {str(e)}\n详细信息: {error_details}"

@tool
def competitor_analysis_tool(category: str, platform: str = "淘宝") -> str:
    """
    分析指定品类在特定平台上的竞争情况。

    Args:
        category: 产品品类，如"面膜"、"手机壳"等
        platform: 目标平台，默认"淘宝"，可选"拼多多"、"京东"等

    Returns:
        竞品分析结果的JSON格式字符串
    """
    try:
        from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

        # 设置超时时间
        SEARCH_TIMEOUT = 12

        def search_competitors():
            # 构建搜索关键词
            search_query = f"{platform} {category} 销量排行"

            # 使用网络搜索获取竞品信息
            ctx = new_context(method="search.competitor")
            client = SearchClient(ctx=ctx)

            response = client.web_search(
                query=search_query,
                count=10,  # 减少结果数量
                need_summary=True
            )
            return response

        # 带超时的搜索
        competitors = []
        ai_summary = ""

        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(search_competitors)
                response = future.result(timeout=SEARCH_TIMEOUT)

                # 分析搜索结果
                if response.web_items:
                    for item in response.web_items[:8]:  # 只取前8个
                        competitor = {
                            "title": item.title,
                            "url": item.url,
                            "site_name": item.site_name,
                            "snippet": item.snippet
                        }
                        competitors.append(competitor)

                ai_summary = response.summary if hasattr(response, 'summary') else ""
        except FutureTimeoutError:
            ai_summary = "搜索超时，仅返回部分结果"
        except Exception as e:
            ai_summary = f"搜索出错: {str(e)}"

        # 综合分析
        analysis = {
            "category": category,
            "platform": platform,
            "competitor_count": len(competitors),
            "market_saturation": "高" if len(competitors) > 8 else "中" if len(competitors) > 4 else "低",
            "ai_summary": ai_summary,
            "competitors": competitors,
            "analysis_time": "当前"
        }

        return json.dumps(analysis, ensure_ascii=False, indent=2)

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return f"竞品分析失败: {str(e)}\n详细信息: {error_details}"

@tool
def trend_analysis_tool(category: str, time_range: str = "1m") -> str:
    """
    分析指定品类的市场趋势和热销关键词。

    Args:
        category: 产品品类，如"面膜"、"手机壳"等
        time_range: 时间范围，如"1w"(1周)、"1m"(1个月)、"3m"(3个月)，默认"1m"

    Returns:
        趋势分析结果的JSON格式字符串
    """
    try:
        from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

        # 设置超时时间
        SEARCH_TIMEOUT = 12

        def search_trends():
            # 构建搜索关键词
            search_query = f"{category} 热销趋势 增长率"

            # 使用网络搜索获取趋势信息
            ctx = new_context(method="search.trend")
            client = SearchClient(ctx=ctx)

            response = client.search(
                query=search_query,
                search_type="web_summary",
                count=8,  # 减少结果数量
                time_range=time_range,
                need_summary=True
            )
            return response

        # 带超时的搜索
        results = []
        trend_summary = ""

        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(search_trends)
                response = future.result(timeout=SEARCH_TIMEOUT)

                # 提取趋势信息
                if response.web_items:
                    for item in response.web_items[:6]:  # 只取前6个
                        trend_item = {
                            "title": item.title,
                            "url": item.url,
                            "site_name": item.site_name,
                            "snippet": item.snippet,
                            "publish_time": item.publish_time if hasattr(item, 'publish_time') else ""
                        }
                        results.append(trend_item)

                trend_summary = response.summary if hasattr(response, 'summary') else ""
        except FutureTimeoutError:
            trend_summary = "搜索超时，仅返回部分结果"
        except Exception as e:
            trend_summary = f"搜索出错: {str(e)}"

        # 综合趋势分析
        trend_analysis = {
            "category": category,
            "time_range": time_range,
            "trend_summary": trend_summary,
            "trend_data_count": len(results),
            "trend_results": results
        }

        return json.dumps(trend_analysis, ensure_ascii=False, indent=2)

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return f"趋势分析失败: {str(e)}\n详细信息: {error_details}"

@tool
def supplier_evaluation_tool(category: str, region: str = None, min_price: float = None,
                            max_price: float = None) -> str:
    """
    评估和推荐供应商，基于品类、地区和价格范围。

    Args:
        category: 产品品类
        region: 地区偏好，如"广州"、"浙江"、"义乌"等，可选
        min_price: 最低进货价，可选
        max_price: 最高进货价，可选

    Returns:
        供应商评估结果的JSON格式字符串
    """
    try:
        from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

        # 设置超时时间
        SEARCH_TIMEOUT = 12

        def search_suppliers():
            # 构建搜索关键词
            search_parts = [category, "供应商", "批发"]
            if region:
                search_parts.append(region)
            if min_price and max_price:
                search_parts.append(f"价格{min_price}-{max_price}")

            search_query = " ".join(search_parts)

            # 使用网络搜索获取供应商信息
            ctx = new_context(method="search.supplier")
            client = SearchClient(ctx=ctx)

            response = client.web_search(
                query=search_query,
                count=10,  # 减少结果数量
                need_summary=True
            )
            return response

        # 带超时的搜索
        suppliers = []
        evaluation_summary = ""

        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(search_suppliers)
                response = future.result(timeout=SEARCH_TIMEOUT)

                # 提取供应商信息
                if response.web_items:
                    for item in response.web_items[:8]:  # 只取前8个
                        supplier = {
                            "title": item.title,
                            "url": item.url,
                            "site_name": item.site_name,
                            "snippet": item.snippet,
                            "summary": item.summary if hasattr(item, 'summary') else ""
                        }
                        suppliers.append(supplier)

                evaluation_summary = response.summary if hasattr(response, 'summary') else ""
        except FutureTimeoutError:
            evaluation_summary = "搜索超时，仅返回部分结果"
        except Exception as e:
            evaluation_summary = f"搜索出错: {str(e)}"

        # 供应商评估
        evaluation = {
            "category": category,
            "region": region or "全国",
            "price_range": f"{min_price}-{max_price}" if min_price and max_price else "不限",
            "supplier_count": len(suppliers),
            "evaluation_summary": evaluation_summary,
            "suppliers": suppliers
        }

        return json.dumps(evaluation, ensure_ascii=False, indent=2)

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return f"供应商评估失败: {str(e)}\n详细信息: {error_details}"

@tool
def save_supplier_to_db(name: str, company_name: str = None, contact_person: str = None,
                        contact_phone: str = None, region: str = None, platform: str = None,
                        platform_url: str = None, min_order_quantity: int = None,
                        is_verified: bool = False, rating: float = None,
                        categories: list = None, tags: list = None, notes: str = None) -> str:
    """
    将供应商信息保存到数据库。
    
    Args:
        name: 供应商名称（必填）
        company_name: 公司名称
        contact_person: 联系人
        contact_phone: 联系电话
        region: 所在地区
        platform: 主要平台（如1688、阿里巴巴等）
        platform_url: 平台店铺URL
        min_order_quantity: 最小起订量
        is_verified: 是否为认证供应商
        rating: 评分（0-5分）
        categories: 经营的品类列表
        tags: 标签列表
        notes: 备注信息
    
    Returns:
        保存结果的JSON格式字符串
    """
    try:
        def save_supplier(db):
            mgr = SupplierManager()
            supplier_in = SupplierCreate(
                name=name,
                company_name=company_name,
                contact_person=contact_person,
                contact_phone=contact_phone,
                region=region,
                platform=platform,
                platform_url=platform_url,
                min_order_quantity=min_order_quantity,
                is_verified=is_verified,
                rating=rating,
                categories=categories or [],
                tags=tags or [],
                notes=notes,
                source="智能体搜索"
            )
            supplier = mgr.create_supplier(db, supplier_in)
            db.refresh(supplier)  # 刷新以获取ID
            return {
                "id": supplier.id,
                "name": supplier.name
            }
        
        supplier_data = execute_with_retry(save_supplier, max_retries=3, retry_delay=1)

        result = {
            "success": True,
            "supplier_id": supplier_data["id"],
            "message": f"供应商'{name}'已成功保存到数据库"
        }
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return f"保存供应商失败: {str(e)}\n详细信息: {error_details}"

@tool
def save_product_to_db(supplier_id: int, name: str, category: str = None,
                       purchase_price: float = None, estimated_price: float = None,
                       logistics_cost: float = 0, min_order_quantity: int = None,
                       potential_score: int = None, image_urls: list = None,
                       product_url: str = None, notes: str = None) -> str:
    """
    将产品信息保存到数据库。
    
    Args:
        supplier_id: 供应商ID（必填）
        name: 产品名称（必填）
        category: 产品品类
        purchase_price: 进货价
        estimated_price: 预估销售价
        logistics_cost: 物流费用
        min_order_quantity: 最小起订量
        potential_score: 潜力分数（1-10分）
        image_urls: 产品图片URL列表
        product_url: 产品链接
        notes: 备注
    
    Returns:
        保存结果的JSON格式字符串
    """
    try:
        def save_product(db):
            mgr = SupplierManager()
            product_in = ProductCreate(
                supplier_id=supplier_id,
                name=name,
                category=category,
                purchase_price=purchase_price,
                estimated_price=estimated_price,
                logistics_cost=logistics_cost,
                min_order_quantity=min_order_quantity,
                potential_score=potential_score,
                image_urls=image_urls or [],
                product_url=product_url,
                notes=notes
            )
            product = mgr.create_product(db, product_in)
            db.refresh(product)  # 刷新以获取ID
            return {
                "id": product.id,
                "name": product.name,
                "profit_margin": product.profit_margin,
                "roi": product.roi
            }
        
        product_data = execute_with_retry(save_product, max_retries=3, retry_delay=1)

        result = {
            "success": True,
            "product_id": product_data["id"],
            "supplier_id": supplier_id,
            "profit_margin": product_data["profit_margin"],
            "roi": product_data["roi"],
            "message": f"产品'{name}'已成功保存到数据库"
        }
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return f"保存产品失败: {str(e)}\n详细信息: {error_details}"

@tool
def query_suppliers_from_db(category: str = None, region: str = None, platform: str = None,
                            min_price: float = None, max_price: float = None,
                            limit: int = 20) -> str:
    """
    从数据库查询供应商信息。
    
    Args:
        category: 产品品类
        region: 地区
        platform: 平台
        min_price: 最低价格
        max_price: 最高价格
        limit: 返回数量限制，默认20
    
    Returns:
        查询结果的JSON格式字符串
    """
    try:
        db = get_session()
        try:
            mgr = SupplierManager()
            suppliers = mgr.search_suppliers(
                db=db,
                category=category,
                region=region,
                platform=platform,
                min_price=min_price,
                max_price=max_price,
                skip=0,
                limit=limit
            )
            
            suppliers_data = []
            for sup in suppliers:
                # 处理JSON字段
                categories_data = []
                if sup.categories is not None:
                    try:
                        categories_data = json.loads(sup.categories)
                    except:
                        categories_data = []
                
                tags_data = []
                if sup.tags is not None:
                    try:
                        tags_data = json.loads(sup.tags)
                    except:
                        tags_data = []
                
                sup_data = {
                    "id": sup.id,
                    "name": sup.name,
                    "company_name": sup.company_name,
                    "contact_person": sup.contact_person,
                    "contact_phone": sup.contact_phone,
                    "region": sup.region,
                    "platform": sup.platform,
                    "platform_url": sup.platform_url,
                    "min_order_quantity": sup.min_order_quantity,
                    "is_verified": sup.is_verified,
                    "rating": sup.rating,
                    "categories": categories_data,
                    "tags": tags_data,
                    "status": sup.status
                }
                suppliers_data.append(sup_data)
            
            result = {
                "total": len(suppliers_data),
                "suppliers": suppliers_data
            }
            return json.dumps(result, ensure_ascii=False, indent=2)
        finally:
            db.close()
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return f"查询供应商失败: {str(e)}\n详细信息: {error_details}"

@tool
def save_trend_to_db(category: str, platform: str = None, growth_rate: float = None,
                     hot_keywords: list = None, summary: str = None,
                     trend_type: str = "monthly") -> str:
    """
    将市场趋势数据保存到数据库。
    
    Args:
        category: 品类（必填）
        platform: 平台
        growth_rate: 增长率（%）
        hot_keywords: 热门关键词列表
        summary: 趋势摘要
        trend_type: 趋势类型（monthly/weekly/daily）
    
    Returns:
        保存结果的JSON格式字符串
    """
    try:
        from datetime import datetime
        db = get_session()
        try:
            mgr = SupplierManager()
            trend_in = MarketTrendCreate(
                category=category,
                platform=platform,
                growth_rate=growth_rate,
                hot_keywords=hot_keywords or [],
                summary=summary,
                trend_type=trend_type,
                data_date=datetime.now()
            )
            trend = mgr.create_market_trend(db, trend_in)
            
            result = {
                "success": True,
                "trend_id": trend.id,
                "message": f"趋势数据'{category}'已成功保存到数据库"
            }
            return json.dumps(result, ensure_ascii=False, indent=2)
        finally:
            db.close()
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return f"保存趋势数据失败: {str(e)}\n详细信息: {error_details}"

@tool
def query_trends_from_db(category: str = None, platform: str = None, limit: int = 10) -> str:
    """
    从数据库查询市场趋势数据。
    
    Args:
        category: 品类
        platform: 平台
        limit: 返回数量限制，默认10
    
    Returns:
        查询结果的JSON格式字符串
    """
    try:
        db = get_session()
        try:
            mgr = SupplierManager()
            trends = mgr.get_market_trends(
                db=db,
                category=category,
                platform=platform,
                skip=0,
                limit=limit
            )
            
            trends_data = []
            for trend in trends:
                # 处理JSON字段
                hot_keywords_data = []
                if trend.hot_keywords is not None:
                    try:
                        hot_keywords_data = json.loads(trend.hot_keywords)
                    except:
                        hot_keywords_data = []
                
                # 处理日期字段
                data_date_str = None
                if trend.data_date is not None:
                    try:
                        data_date_str = trend.data_date.isoformat()
                    except:
                        data_date_str = None
                
                trend_data = {
                    "id": trend.id,
                    "category": trend.category,
                    "platform": trend.platform,
                    "growth_rate": trend.growth_rate,
                    "hot_keywords": hot_keywords_data,
                    "summary": trend.summary,
                    "trend_type": trend.trend_type,
                    "data_date": data_date_str
                }
                trends_data.append(trend_data)
            
            result = {
                "total": len(trends_data),
                "trends": trends_data
            }
            return json.dumps(result, ensure_ascii=False, indent=2)
        finally:
            db.close()
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return f"查询趋势数据失败: {str(e)}\n详细信息: {error_details}"

@tool
def search_1688_tool(keyword: str, category: str = None, min_price: float = None,
                      max_price: float = None, count: int = 10) -> str:
    """
    在1688平台上搜索供应商和产品信息。

    Args:
        keyword: 搜索关键词，如"面膜"、"手机壳"等
        category: 产品品类，用于更精确的搜索
        min_price: 最低进货价
        max_price: 最高进货价
        count: 返回结果数量，默认10条，最大20条

    Returns:
        1688搜索结果的JSON格式字符串
    """
    try:
        from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

        # 限制返回结果数量
        count = min(count, 20)

        # 设置超时时间
        SEARCH_TIMEOUT = 12

        def search_1688():
            # 构建搜索查询
            search_parts = ["1688", keyword]
            if category:
                search_parts.append(category)
            if min_price and max_price:
                search_parts.append(f"价格{min_price}-{max_price}")
            search_parts.append("批发")

            search_query = " ".join(search_parts)

            ctx = new_context(method="search.1688")
            client = SearchClient(ctx=ctx)

            response = client.search(
                query=search_query,
                search_type="web_summary",
                count=count,
                sites="1688.com",
                need_summary=True
            )
            return response

        # 带超时的搜索
        results = []
        ai_summary = ""

        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(search_1688)
                response = future.result(timeout=SEARCH_TIMEOUT)

                if response.web_items:
                    for item in response.web_items:
                        result = {
                            "title": item.title,
                            "url": item.url,
                            "snippet": item.snippet,
                            "site_name": item.site_name,
                            "summary": item.summary if hasattr(item, 'summary') else ""
                        }
                        results.append(result)

                ai_summary = response.summary if hasattr(response, 'summary') else ""
        except FutureTimeoutError:
            ai_summary = "搜索超时，仅返回部分结果"
        except Exception as e:
            ai_summary = f"搜索出错: {str(e)}"

        output = {
            "platform": "1688",
            "keyword": keyword,
            "total_results": len(results),
            "ai_summary": ai_summary,
            "results": results
        }

        return json.dumps(output, ensure_ascii=False, indent=2)

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return f"1688搜索失败: {str(e)}\n详细信息: {error_details}"


@tool
def search_alibaba_tool(keyword: str, category: str = None, min_price: float = None,
                        max_price: float = None, count: int = 10) -> str:
    """
    在阿里巴巴国际站上搜索供应商和产品信息。

    Args:
        keyword: 搜索关键词
        category: 产品品类
        min_price: 最低进货价
        max_price: 最高进货价
        count: 返回结果数量，默认10条，最大20条

    Returns:
        阿里巴巴搜索结果的JSON格式字符串
    """
    try:
        from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

        # 限制返回结果数量
        count = min(count, 20)

        # 设置超时时间
        SEARCH_TIMEOUT = 12

        def search_alibaba():
            search_parts = ["alibaba", keyword]
            if category:
                search_parts.append(category)
            if min_price and max_price:
                search_parts.append(f"price{min_price}-{max_price}")
            search_parts.append("wholesale")

            search_query = " ".join(search_parts)

            ctx = new_context(method="search.alibaba")
            client = SearchClient(ctx=ctx)

            response = client.search(
                query=search_query,
                search_type="web_summary",
                count=count,
                sites="alibaba.com",
                need_summary=True
            )
            return response

        # 带超时的搜索
        results = []
        ai_summary = ""

        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(search_alibaba)
                response = future.result(timeout=SEARCH_TIMEOUT)

                if response.web_items:
                    for item in response.web_items:
                        result = {
                            "title": item.title,
                            "url": item.url,
                            "snippet": item.snippet,
                            "site_name": item.site_name,
                            "summary": item.summary if hasattr(item, 'summary') else ""
                        }
                        results.append(result)

                ai_summary = response.summary if hasattr(response, 'summary') else ""
        except FutureTimeoutError:
            ai_summary = "搜索超时，仅返回部分结果"
        except Exception as e:
            ai_summary = f"搜索出错: {str(e)}"

        output = {
            "platform": "阿里巴巴",
            "keyword": keyword,
            "total_results": len(results),
            "ai_summary": ai_summary,
            "results": results
        }

        return json.dumps(output, ensure_ascii=False, indent=2)

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return f"阿里巴巴搜索失败: {str(e)}\n详细信息: {error_details}"


@tool
def save_user_preference(user_id: str, preferred_categories: list = None,
                         min_price: float = None, max_price: float = None,
                         preferred_platforms: list = None, preferred_regions: list = None,
                         min_roi: float = None, min_profit_margin: float = None,
                         keywords: list = None, exclude_keywords: list = None,
                         notification_enabled: bool = True) -> str:
    """
    保存或更新用户偏好设置。
    
    Args:
        user_id: 用户ID（必填）
        preferred_categories: 偏好品类列表
        min_price: 最低进货价
        max_price: 最高进货价
        preferred_platforms: 偏好平台列表
        preferred_regions: 偏好地区列表
        min_roi: 最低ROI要求（%）
        min_profit_margin: 最低利润率要求（%）
        keywords: 关注关键词列表
        exclude_keywords: 排除关键词列表
        notification_enabled: 是否启用通知
    
    Returns:
        保存结果的JSON格式字符串
    """
    try:
        db = get_session()
        try:
            mgr = SupplierManager()
            pref = mgr.create_or_update_preference(
                db=db,
                user_id=user_id,
                preferred_categories=preferred_categories,
                min_price=min_price,
                max_price=max_price,
                preferred_platforms=preferred_platforms,
                preferred_regions=preferred_regions,
                min_roi=min_roi,
                min_profit_margin=min_profit_margin,
                keywords=keywords,
                exclude_keywords=exclude_keywords,
                notification_enabled=notification_enabled
            )
            
            result = {
                "success": True,
                "user_id": user_id,
                "message": "用户偏好已成功保存",
                "preferences": {
                    "preferred_categories": preferred_categories or [],
                    "min_price": min_price,
                    "max_price": max_price,
                    "preferred_platforms": preferred_platforms or [],
                    "preferred_regions": preferred_regions or [],
                    "min_roi": min_roi,
                    "min_profit_margin": min_profit_margin,
                    "notification_enabled": notification_enabled
                }
            }
            return json.dumps(result, ensure_ascii=False, indent=2)
        finally:
            db.close()
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return f"保存用户偏好失败: {str(e)}\n详细信息: {error_details}"


@tool
def get_user_preference(user_id: str) -> str:
    """
    获取用户的偏好设置。
    
    Args:
        user_id: 用户ID（必填）
    
    Returns:
        用户偏好设置的JSON格式字符串
    """
    try:
        db = get_session()
        try:
            mgr = SupplierManager()
            pref = mgr.get_user_preference(db, user_id)
            
            if not pref:
                result = {
                    "success": False,
                    "message": "未找到用户偏好设置"
                }
                return json.dumps(result, ensure_ascii=False, indent=2)
            
            # 解析JSON字段
            categories = []
            if pref.preferred_categories is not None:
                try:
                    categories = json.loads(pref.preferred_categories)
                except:
                    pass
            
            platforms = []
            if pref.preferred_platforms is not None:
                try:
                    platforms = json.loads(pref.preferred_platforms)
                except:
                    pass
            
            regions = []
            if pref.preferred_regions is not None:
                try:
                    regions = json.loads(pref.preferred_regions)
                except:
                    pass
            
            keywords = []
            if pref.keywords is not None:
                try:
                    keywords = json.loads(pref.keywords)
                except:
                    pass
            
            exclude_keywords = []
            if pref.exclude_keywords is not None:
                try:
                    exclude_keywords = json.loads(pref.exclude_keywords)
                except:
                    pass
            
            result = {
                "success": True,
                "user_id": user_id,
                "preferences": {
                    "preferred_categories": categories,
                    "min_price": pref.min_price,
                    "max_price": pref.max_price,
                    "preferred_platforms": platforms,
                    "preferred_regions": regions,
                    "min_roi": pref.min_roi,
                    "min_profit_margin": pref.min_profit_margin,
                    "keywords": keywords,
                    "exclude_keywords": exclude_keywords,
                    "notification_enabled": pref.notification_enabled
                },
                "created_at": pref.created_at.isoformat() if pref.created_at is not None else None,
                "updated_at": pref.updated_at.isoformat() if pref.updated_at is not None else None
            }
            return json.dumps(result, ensure_ascii=False, indent=2)
        finally:
            db.close()
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return f"获取用户偏好失败: {str(e)}\n详细信息: {error_details}"


@tool
def batch_import_suppliers(suppliers_data: list, source: str = "batch_import") -> str:
    """
    批量导入供应商数据到数据库。
    
    Args:
        suppliers_data: 供应商数据列表，每个元素是一个字典，包含供应商信息
        source: 数据来源，默认"batch_import"
    
    Returns:
        批量导入结果的JSON格式字符串
    """
    try:
        db = get_session()
        try:
            mgr = SupplierManager()
            result = mgr.batch_import_suppliers(db, suppliers_data, source)
            return json.dumps(result, ensure_ascii=False, indent=2)
        finally:
            db.close()
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return f"批量导入失败: {str(e)}\n详细信息: {error_details}"


@tool
def smart_recommend_products(user_id: str, limit: int = 10) -> str:
    """
    基于用户偏好和历史数据智能推荐产品。
    
    Args:
        user_id: 用户ID（必填）
        limit: 返回推荐数量，默认10个
    
    Returns:
        产品推荐列表的JSON格式字符串
    """
    try:
        db = get_session()
        try:
            mgr = SupplierManager()
            products = mgr.recommend_products(db, user_id, limit)
            
            products_data = []
            for prod in products:
                # 处理JSON字段
                image_urls = []
                if prod.image_urls is not None:
                    try:
                        image_urls = json.loads(prod.image_urls)
                    except:
                        pass
                
                tags = []
                if prod.tags is not None:
                    try:
                        tags = json.loads(prod.tags)
                    except:
                        pass
                
                # 获取供应商信息
                supplier = mgr.get_supplier_by_id(db, prod.supplier_id)
                supplier_name = supplier.name if supplier else "未知"
                supplier_platform = supplier.platform if supplier else ""
                
                prod_data = {
                    "id": prod.id,
                    "name": prod.name,
                    "category": prod.category,
                    "supplier_id": prod.supplier_id,
                    "supplier_name": supplier_name,
                    "supplier_platform": supplier_platform,
                    "purchase_price": prod.purchase_price,
                    "estimated_price": prod.estimated_price,
                    "profit_margin": prod.profit_margin,
                    "roi": prod.roi,
                    "potential_score": prod.potential_score,
                    "image_urls": image_urls,
                    "tags": tags,
                    "notes": prod.notes
                }
                products_data.append(prod_data)
            
            result = {
                "user_id": user_id,
                "total": len(products_data),
                "products": products_data
            }
            return json.dumps(result, ensure_ascii=False, indent=2)
        finally:
            db.close()
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return f"智能推荐失败: {str(e)}\n详细信息: {error_details}"


@tool
def generate_trend_chart(category: str = None, platform: str = None, days: int = 30) -> str:
    """
    生成市场趋势图表数据（用于数据可视化）。
    
    Args:
        category: 产品品类
        platform: 平台
        days: 分析天数，默认30天
    
    Returns:
        趋势图表数据的JSON格式字符串，包含时间序列数据
    """
    try:
        db = get_session()
        try:
            mgr = SupplierManager()
            
            # 获取趋势数据
            trends = mgr.get_market_trends(db, category, platform, skip=0, limit=days)
            
            # 生成图表数据
            chart_data = {
                "category": category or "所有品类",
                "platform": platform or "所有平台",
                "days": days,
                "time_series": [],
                "summary": {
                    "avg_growth_rate": 0,
                    "max_growth_rate": 0,
                    "min_growth_rate": 0,
                    "total_trends": len(trends)
                }
            }
            
            growth_rates = []
            for trend in trends:
                trend_data = {
                    "date": trend.data_date.isoformat() if trend.data_date is not None else None,
                    "growth_rate": trend.growth_rate,
                    "hot_keywords": json.loads(trend.hot_keywords) if trend.hot_keywords is not None else [],
                    "summary": trend.summary
                }
                chart_data["time_series"].append(trend_data)
                
                if trend.growth_rate is not None:
                    growth_rates.append(trend.growth_rate)
            
            # 计算统计数据
            if growth_rates:
                chart_data["summary"]["avg_growth_rate"] = round(sum(growth_rates) / len(growth_rates), 2)
                chart_data["summary"]["max_growth_rate"] = round(max(growth_rates), 2)
                chart_data["summary"]["min_growth_rate"] = round(min(growth_rates), 2)
            
            return json.dumps(chart_data, ensure_ascii=False, indent=2)
        finally:
            db.close()
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return f"生成趋势图表失败: {str(e)}\n详细信息: {error_details}"


@tool
def get_notifications(user_id: str, is_read: bool = None, limit: int = 20) -> str:
    """
    获取用户的通知列表。
    
    Args:
        user_id: 用户ID（必填）
        is_read: 是否已读（None=全部, True=已读, False=未读）
        limit: 返回数量限制，默认20条
    
    Returns:
        通知列表的JSON格式字符串
    """
    try:
        db = get_session()
        try:
            mgr = SupplierManager()
            notifications = mgr.get_notifications(db, user_id, is_read, skip=0, limit=limit)
            
            notifications_data = []
            for notif in notifications:
                # 解析附加数据
                data = {}
                if notif.data is not None:
                    try:
                        data = json.loads(notif.data)
                    except:
                        pass
                
                notif_data = {
                    "id": notif.id,
                    "notification_type": notif.notification_type,
                    "title": notif.title,
                    "content": notif.content,
                    "data": data,
                    "priority": notif.priority,
                    "is_read": notif.is_read,
                    "created_at": notif.created_at.isoformat() if notif.created_at is not None else None,
                    "read_at": notif.read_at.isoformat() if notif.read_at is not None else None
                }
                notifications_data.append(notif_data)
            
            result = {
                "user_id": user_id,
                "total": len(notifications_data),
                "notifications": notifications_data
            }
            return json.dumps(result, ensure_ascii=False, indent=2)
        finally:
            db.close()
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return f"获取通知失败: {str(e)}\n详细信息: {error_details}"


@tool
def create_trend_notification(user_id: str, category: str, growth_rate: float,
                               summary: str, hot_keywords: list = None) -> str:
    """
    创建趋势警报通知。
    
    Args:
        user_id: 用户ID（必填）
        category: 品类
        growth_rate: 增长率（%）
        summary: 趋势摘要
        hot_keywords: 热门关键词列表
    
    Returns:
        通知创建结果的JSON格式字符串
    """
    try:
        db = get_session()
        try:
            mgr = SupplierManager()
            notification = mgr.create_trend_alert(
                db=db,
                user_id=user_id,
                category=category,
                growth_rate=growth_rate,
                summary=summary,
                hot_keywords=hot_keywords or []
            )
            
            result = {
                "success": True,
                "notification_id": notification.id,
                "title": notification.title,
                "priority": notification.priority,
                "message": "趋势警报通知已创建"
            }
            return json.dumps(result, ensure_ascii=False, indent=2)
        finally:
            db.close()
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return f"创建趋势通知失败: {str(e)}\n详细信息: {error_details}"


@tool
def parse_product_link(product_url: str, analysis_depth: str = "standard") -> str:
    """
    分析淘宝/拼多多产品链接，获取产品详细信息并进行市场分析。

    Args:
        product_url: 产品链接（淘宝/拼多多），如 https://item.taobao.com/item.htm?id=123456
        analysis_depth: 分析深度（quick/standard/deep），默认standard
                        - quick: 快速分析，只获取基本信息
                        - standard: 标准分析，包含货源和竞品搜索（默认）
                        - deep: 深度分析（当前等同于standard）

    Returns:
        产品分析结果的JSON格式字符串，包含产品信息、市场分析、货源建议等
    """
    try:
        import re
        from datetime import datetime
        from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
        from coze_coding_dev_sdk import get_session
        from storage.database.shared.model import ProductLinkAnalysis

        # 设置超时时间（秒）
        MAIN_SEARCH_TIMEOUT = 15
        SECONDARY_SEARCH_TIMEOUT = 10

        # 1. 识别平台
        platform = None
        product_id = None

        if "taobao.com" in product_url or "tmall.com" in product_url:
            platform = "taobao"
            # 提取商品ID
            id_match = re.search(r'id=(\d+)', product_url)
            if id_match:
                product_id = id_match.group(1)
        elif "yangkeduo.com" in product_url or "pinduoduo.com" in product_url or "m.pinduoduo.com" in product_url:
            platform = "pinduoduo"
            # 提取商品ID
            id_match = re.search(r'goods[_]?id=(\d+)', product_url)
            if id_match:
                product_id = id_match.group(1)
        elif "jd.com" in product_url:
            platform = "jd"
            # 提取商品ID
            id_match = re.search(r'/(\d+)\.html', product_url)
            if id_match:
                product_id = id_match.group(1)
        else:
            return json.dumps({
                "success": False,
                "error": "不支持的平台链接，仅支持淘宝、拼多多、京东"
            }, ensure_ascii=False, indent=2)

        # 2. 使用网络搜索获取产品信息（带超时）
        def get_product_info():
            search_query = f"{product_url} 产品详情"
            ctx = new_context(method="search.product")
            client = SearchClient(ctx=ctx)
            response = client.web_search(
                query=search_query,
                count=10,
                need_summary=True
            )
            return response

        product_info = {
            "platform": platform,
            "product_id": product_id,
            "product_url": product_url
        }

        # 带超时的搜索
        search_results = []
        category = "其他"

        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(get_product_info)
                response = future.result(timeout=MAIN_SEARCH_TIMEOUT)

                # 从搜索结果中提取信息
                if response.web_items:
                    for item in response.web_items[:5]:  # 只取前5个结果
                        search_results.append({
                            "title": item.title,
                            "url": item.url,
                            "snippet": item.snippet,
                            "site_name": item.site_name
                        })

                # 从标题中提取产品名称和品类
                if search_results:
                    first_title = search_results[0]["title"]
                    product_info["product_title"] = first_title[:200]  # 限制长度
                    product_info["ai_summary"] = response.summary if hasattr(response, 'summary') else ""

                    # 提取品类
                    common_categories = ["面膜", "手机壳", "衣服", "鞋", "包", "食品", "化妆品", "数码", "家电", "家居", "母婴", "运动"]
                    for cat in common_categories:
                        if cat in first_title:
                            category = cat
                            break
                    product_info["category"] = category
        except FutureTimeoutError:
            # 主搜索超时，使用默认值
            product_info["search_timeout"] = True
            product_info["ai_summary"] = "产品信息搜索超时，建议稍后重试"
        except Exception as e:
            product_info["search_error"] = str(e)

        # 3. 如果是快速分析模式，跳过货源和竞品搜索
        if analysis_depth == "quick":
            analysis_result = {
                "success": True,
                "product_info": product_info,
                "market_analysis": {
                    "category": category,
                    "competitor_count": 0,
                    "sourcing_count": 0,
                    "analysis_depth": "quick"
                },
                "sourcing_opportunities": [],
                "competitors": [],
                "analysis_summary": f"快速分析完成：{platform}平台产品链接，识别为{category}品类。",
                "analyzed_at": datetime.now().isoformat()
            }
            return json.dumps(analysis_result, ensure_ascii=False, indent=2)

        # 4. 标准分析：搜索货源和竞品（带超时，可并行）
        sourcing_results = []
        competitor_results = []

        def search_sourcing():
            sourcing_query = f"1688 {category} 同款 批发"
            ctx = new_context(method="search.sourcing")
            client = SearchClient(ctx=ctx)
            response = client.search(
                query=sourcing_query,
                search_type="web_summary",
                count=5,  # 减少结果数量
                sites="1688.com",
                need_summary=True
            )
            results = []
            if response.web_items:
                for item in response.web_items:
                    results.append({
                        "source": "1688",
                        "title": item.title,
                        "url": item.url,
                        "snippet": item.snippet
                    })
            return results

        def search_competitors():
            competitor_query = f"淘宝 {category} 热销"
            ctx = new_context(method="search.competitor")
            client = SearchClient(ctx=ctx)
            response = client.search(
                query=competitor_query,
                search_type="web_summary",
                count=5,  # 减少结果数量
                need_summary=True
            )
            results = []
            if response.web_items:
                for item in response.web_items:
                    results.append({
                        "title": item.title,
                        "url": item.url,
                        "snippet": item.snippet
                    })
            return results

        # 并行执行货源和竞品搜索
        try:
            with ThreadPoolExecutor(max_workers=2) as executor:
                future_sourcing = executor.submit(search_sourcing)
                future_competitors = executor.submit(search_competitors)

                try:
                    sourcing_results = future_sourcing.result(timeout=SECONDARY_SEARCH_TIMEOUT)
                except FutureTimeoutError:
                    pass

                try:
                    competitor_results = future_competitors.result(timeout=SECONDARY_SEARCH_TIMEOUT)
                except FutureTimeoutError:
                    pass
        except Exception as e:
            # 搜索失败不影响主流程
            pass

        # 5. 综合分析结果
        analysis_result = {
            "success": True,
            "product_info": product_info,
            "market_analysis": {
                "category": category,
                "competitor_count": len(competitor_results),
                "sourcing_count": len(sourcing_results),
                "analysis_depth": analysis_depth
            },
            "sourcing_opportunities": sourcing_results,
            "competitors": competitor_results,
            "analysis_summary": f"已成功分析{platform}平台产品链接，识别为{category}品类，找到{len(sourcing_results)}个潜在货源和{len(competitor_results)}个竞品。",
            "analyzed_at": datetime.now().isoformat()
        }

        # 6. 保存分析结果到数据库（异步，不阻塞返回）
        def save_analysis(db):
            try:
                analysis = ProductLinkAnalysis(
                    original_url=product_url,
                    platform=platform,
                    product_id=product_id,
                    product_title=product_info.get("product_title"),
                    category=category,
                    market_analysis=json.dumps(analysis_result["market_analysis"], ensure_ascii=False),
                    competitor_info=json.dumps(competitor_results[:5], ensure_ascii=False),
                    sourcing_suggestions=json.dumps(sourcing_results[:5], ensure_ascii=False),
                    analysis_summary=analysis_result["analysis_summary"],
                    potential_score=min(10, len(sourcing_results) // 2 + 5),
                    status="analyzed",
                    analyzed_at=datetime.now()
                )
                db.add(analysis)
                db.commit()
                db.refresh(analysis)
                return analysis.id
            except Exception as e:
                # 数据库保存失败不影响主流程
                return None

        try:
            analysis_id = execute_with_retry(save_analysis, max_retries=2, retry_delay=0.5)
            if analysis_id:
                analysis_result["database_id"] = analysis_id
                analysis_result["saved_to_db"] = True
        except Exception as e:
            analysis_result["saved_to_db"] = False
            analysis_result["db_error"] = str(e)

        return json.dumps(analysis_result, ensure_ascii=False, indent=2)

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return json.dumps({
            "success": False,
            "error": f"产品链接分析失败: {str(e)}",
            "details": error_details
        }, ensure_ascii=False, indent=2)


@tool
def parse_shop_link(shop_url: str, analysis_depth: str = "standard") -> str:
    """
    分析淘宝/拼多多店铺链接，获取店铺详细信息并进行市场分析。

    Args:
        shop_url: 店铺链接（淘宝/拼多多），如 https://shop12345.taobao.com
        analysis_depth: 分析深度（quick/standard/deep），默认standard
                        - quick: 快速分析，只获取基本信息
                        - standard: 标准分析，包含热销产品和货源搜索（默认）
                        - deep: 深度分析（当前等同于standard）

    Returns:
        店铺分析结果的JSON格式字符串，包含店铺信息、产品分析、货源机会等
    """
    try:
        import re
        from datetime import datetime
        from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
        from coze_coding_dev_sdk import get_session
        from storage.database.shared.model import ShopLinkAnalysis

        # 设置超时时间（秒）
        MAIN_SEARCH_TIMEOUT = 15
        SECONDARY_SEARCH_TIMEOUT = 10

        # 1. 识别平台
        platform = None
        shop_id = None

        if "taobao.com" in shop_url or "tmall.com" in shop_url:
            platform = "taobao"
            # 提取店铺ID
            id_match = re.search(r'shop(\d+)', shop_url)
            if id_match:
                shop_id = id_match.group(1)
            else:
                # 尝试从URL中提取
                id_match = re.search(r'shop_id=(\d+)', shop_url)
                if id_match:
                    shop_id = id_match.group(1)
        elif "yangkeduo.com" in shop_url or "pinduoduo.com" in shop_url or "m.pinduoduo.com" in shop_url:
            platform = "pinduoduo"
            # 提取店铺ID
            id_match = re.search(r'mall[_]?id=(\d+)', shop_url)
            if id_match:
                shop_id = id_match.group(1)
        elif "jd.com" in shop_url:
            platform = "jd"
            # 提取店铺ID
            id_match = re.search(r'shop[_]?id=(\d+)', shop_url)
            if id_match:
                shop_id = id_match.group(1)
        else:
            return json.dumps({
                "success": False,
                "error": "不支持的平台链接，仅支持淘宝、拼多多、京东"
            }, ensure_ascii=False, indent=2)

        # 2. 使用网络搜索获取店铺信息（带超时）
        def get_shop_info():
            search_query = f"{shop_url} 店铺信息"
            ctx = new_context(method="search.shop")
            client = SearchClient(ctx=ctx)
            response = client.web_search(
                query=search_query,
                count=10,
                need_summary=True
            )
            return response

        shop_info = {
            "platform": platform,
            "shop_id": shop_id,
            "shop_url": shop_url
        }

        # 带超时的搜索
        search_results = []
        main_category = "未知"

        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(get_shop_info)
                response = future.result(timeout=MAIN_SEARCH_TIMEOUT)

                # 从搜索结果中提取信息
                if response.web_items:
                    for item in response.web_items[:5]:  # 只取前5个结果
                        search_results.append({
                            "title": item.title,
                            "url": item.url,
                            "snippet": item.snippet,
                            "site_name": item.site_name
                        })

                # 从标题中提取店铺名称和品类
                if search_results:
                    first_title = search_results[0]["title"]
                    shop_info["shop_name"] = first_title[:100]  # 限制长度
                    shop_info["ai_summary"] = response.summary if hasattr(response, 'summary') else ""

                    # 推断店铺类型
                    shop_types = ["旗舰店", "专营店", "专卖店", "官方店"]
                    for shop_type in shop_types:
                        if shop_type in first_title:
                            shop_info["shop_type"] = shop_type
                            break

                    # 推断主营品类
                    common_categories = ["美妆", "服饰", "数码", "家电", "食品", "家居", "母婴", "运动"]
                    for cat in common_categories:
                        if cat in first_title:
                            main_category = cat
                            break

                    shop_info["main_category"] = main_category
        except FutureTimeoutError:
            # 主搜索超时，使用默认值
            shop_info["search_timeout"] = True
            shop_info["ai_summary"] = "店铺信息搜索超时，建议稍后重试"
        except Exception as e:
            shop_info["search_error"] = str(e)

        # 3. 如果是快速分析模式，跳过产品搜索
        if analysis_depth == "quick":
            analysis_result = {
                "success": True,
                "shop_info": shop_info,
                "top_products": [],
                "market_position": {
                    "category": main_category,
                    "platform": platform,
                    "product_count": 0,
                    "sourcing_count": 0
                },
                "sourcing_opportunities": [],
                "analysis_summary": f"快速分析完成：{platform}平台店铺链接，识别为{main_category}品类店铺。",
                "analyzed_at": datetime.now().isoformat()
            }
            return json.dumps(analysis_result, ensure_ascii=False, indent=2)

        # 4. 标准分析：搜索热销产品和货源（带超时，可并行）
        top_products = []
        sourcing_opportunities = []

        def search_products():
            product_search_query = f"{shop_url} 热销产品"
            ctx = new_context(method="search.shop_products")
            client = SearchClient(ctx=ctx)
            response = client.search(
                query=product_search_query,
                search_type="web_summary",
                count=5,  # 减少结果数量
                need_summary=True
            )
            results = []
            if response.web_items:
                for idx, item in enumerate(response.web_items[:3], 1):  # 只取前3个
                    results.append({
                        "rank": idx,
                        "title": item.title,
                        "url": item.url,
                        "snippet": item.snippet
                    })
            return results

        def search_sourcing():
            sourcing_query = f"1688 {main_category} 店铺货源"
            ctx = new_context(method="search.sourcing")
            client = SearchClient(ctx=ctx)
            response = client.search(
                query=sourcing_query,
                search_type="web_summary",
                count=5,  # 减少结果数量
                sites="1688.com",
                need_summary=True
            )
            results = []
            if response.web_items:
                for item in response.web_items:
                    results.append({
                        "source": "1688",
                        "title": item.title,
                        "url": item.url,
                        "snippet": item.snippet
                    })
            return results

        # 并行执行产品和货源搜索
        try:
            with ThreadPoolExecutor(max_workers=2) as executor:
                future_products = executor.submit(search_products)
                future_sourcing = executor.submit(search_sourcing)

                try:
                    top_products = future_products.result(timeout=SECONDARY_SEARCH_TIMEOUT)
                except FutureTimeoutError:
                    pass

                try:
                    sourcing_opportunities = future_sourcing.result(timeout=SECONDARY_SEARCH_TIMEOUT)
                except FutureTimeoutError:
                    pass
        except Exception as e:
            # 搜索失败不影响主流程
            pass

        # 5. 综合分析结果
        market_position = {
            "category": main_category,
            "platform": platform,
            "product_count": len(top_products),
            "sourcing_count": len(sourcing_opportunities)
        }

        analysis_result = {
            "success": True,
            "shop_info": shop_info,
            "top_products": top_products,
            "market_position": market_position,
            "sourcing_opportunities": sourcing_opportunities,
            "analysis_summary": f"已成功分析{platform}平台店铺链接，识别为{main_category}品类店铺，发现{len(top_products)}个热销产品和{len(sourcing_opportunities)}个潜在货源机会。",
            "analyzed_at": datetime.now().isoformat()
        }

        # 6. 保存分析结果到数据库（异步，不阻塞返回）
        def save_analysis(db):
            try:
                analysis = ShopLinkAnalysis(
                    original_url=shop_url,
                    platform=platform,
                    shop_id=shop_id,
                    shop_name=shop_info.get("shop_name"),
                    shop_type=shop_info.get("shop_type"),
                    main_category=main_category,
                    product_count=len(top_products),
                    top_products=json.dumps(top_products, ensure_ascii=False),
                    market_position=json.dumps(market_position, ensure_ascii=False),
                    sourcing_opportunities=json.dumps(sourcing_opportunities[:5], ensure_ascii=False),
                    analysis_summary=analysis_result["analysis_summary"],
                    status="analyzed",
                    analyzed_at=datetime.now()
                )
                db.add(analysis)
                db.commit()
                db.refresh(analysis)
                return analysis.id
            except Exception as e:
                # 数据库保存失败不影响主流程
                return None

        try:
            analysis_id = execute_with_retry(save_analysis, max_retries=2, retry_delay=0.5)
            if analysis_id:
                analysis_result["database_id"] = analysis_id
                analysis_result["saved_to_db"] = True
        except Exception as e:
            analysis_result["saved_to_db"] = False
            analysis_result["db_error"] = str(e)

        return json.dumps(analysis_result, ensure_ascii=False, indent=2)

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return json.dumps({
            "success": False,
            "error": f"店铺链接分析失败: {str(e)}",
            "details": error_details
        }, ensure_ascii=False, indent=2)


def build_agent(ctx=None):
    workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
    config_path = os.path.join(workspace_path, LLM_CONFIG)
    
    with open(config_path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    
    api_key = os.getenv("COZE_WORKLOAD_IDENTITY_API_KEY")
    base_url = os.getenv("COZE_INTEGRATION_MODEL_BASE_URL")
    
    llm = ChatOpenAI(
        model=cfg['config'].get("model"),
        api_key=api_key,
        base_url=base_url,
        temperature=cfg['config'].get('temperature', 0.7),
        streaming=True,
        timeout=cfg['config'].get('timeout', 600),
        extra_body={
            "thinking": {
                "type": cfg['config'].get('thinking', 'disabled')
            }
        },
        default_headers=default_headers(ctx) if ctx else {}
    )
    
    # 定义工具列表
    tools = [
        # 搜索工具
        web_search_tool,
        advanced_search_tool,
        image_search_tool,
        search_1688_tool,
        search_alibaba_tool,
        # 分析工具
        roi_calculator_tool,
        competitor_analysis_tool,
        trend_analysis_tool,
        supplier_evaluation_tool,
        # 数据库工具
        save_supplier_to_db,
        save_product_to_db,
        query_suppliers_from_db,
        save_trend_to_db,
        query_trends_from_db,
        # 用户偏好工具
        save_user_preference,
        get_user_preference,
        # 批量操作工具
        batch_import_suppliers,
        # 智能推荐工具
        smart_recommend_products,
        # 可视化工具
        generate_trend_chart,
        # 通知工具
        get_notifications,
        create_trend_notification,
        # 链接分析工具
        parse_product_link,
        parse_shop_link
    ]
    
    return create_agent(
        model=llm,
        system_prompt=cfg.get("sp"),
        tools=tools,
        checkpointer=get_memory_saver(),
        state_schema=AgentState,
    )
