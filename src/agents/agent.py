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
from storage.database.supplier_manager import (
    SupplierManager, SupplierCreate, ProductCreate, 
    ProductUpdate, MarketTrendCreate
)
from storage.database.shared.model import Supplier, Product, MarketTrend

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
        # 构建搜索关键词
        search_query = f"{platform} {category} 销量排行 竞品分析"
        
        # 使用网络搜索获取竞品信息
        ctx = new_context(method="search.competitor")
        client = SearchClient(ctx=ctx)
        
        response = client.web_search(
            query=search_query,
            count=15,
            need_summary=True
        )
        
        # 分析搜索结果
        competitors = []
        if response.web_items:
            for item in response.web_items:
                competitor = {
                    "title": item.title,
                    "url": item.url,
                    "site_name": item.site_name,
                    "snippet": item.snippet
                }
                competitors.append(competitor)
        
        # 综合分析
        analysis = {
            "category": category,
            "platform": platform,
            "competitor_count": len(competitors),
            "market_saturation": "高" if len(competitors) > 10 else "中" if len(competitors) > 5 else "低",
            "ai_summary": response.summary if hasattr(response, 'summary') else "",
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
        # 构建搜索关键词
        search_query = f"{category} 热销趋势 增长率 市场分析"
        
        # 使用网络搜索获取趋势信息
        ctx = new_context(method="search.trend")
        client = SearchClient(ctx=ctx)
        
        response = client.search(
            query=search_query,
            search_type="web_summary",
            count=10,
            time_range=time_range,
            need_summary=True
        )
        
        # 提取趋势信息
        results = []
        if response.web_items:
            for item in response.web_items:
                trend_item = {
                    "title": item.title,
                    "url": item.url,
                    "site_name": item.site_name,
                    "snippet": item.snippet,
                    "publish_time": item.publish_time if hasattr(item, 'publish_time') else ""
                }
                results.append(trend_item)
        
        # 综合趋势分析
        trend_analysis = {
            "category": category,
            "time_range": time_range,
            "trend_summary": response.summary if hasattr(response, 'summary') else "",
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
            count=15,
            need_summary=True
        )
        
        # 提取供应商信息
        suppliers = []
        if response.web_items:
            for item in response.web_items:
                supplier = {
                    "title": item.title,
                    "url": item.url,
                    "site_name": item.site_name,
                    "snippet": item.snippet,
                    "summary": item.summary if hasattr(item, 'summary') else ""
                }
                suppliers.append(supplier)
        
        # 供应商评估
        evaluation = {
            "category": category,
            "region": region or "全国",
            "price_range": f"{min_price}-{max_price}" if min_price and max_price else "不限",
            "supplier_count": len(suppliers),
            "evaluation_summary": response.summary if hasattr(response, 'summary') else "",
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
        db = get_session()
        try:
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
            
            result = {
                "success": True,
                "supplier_id": supplier.id,
                "message": f"供应商'{name}'已成功保存到数据库"
            }
            return json.dumps(result, ensure_ascii=False, indent=2)
        finally:
            db.close()
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
        db = get_session()
        try:
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
            
            result = {
                "success": True,
                "product_id": product.id,
                "supplier_id": supplier_id,
                "profit_margin": product.profit_margin,
                "roi": product.roi,
                "message": f"产品'{name}'已成功保存到数据库"
            }
            return json.dumps(result, ensure_ascii=False, indent=2)
        finally:
            db.close()
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
        web_search_tool,
        advanced_search_tool,
        image_search_tool,
        roi_calculator_tool,
        competitor_analysis_tool,
        trend_analysis_tool,
        supplier_evaluation_tool,
        save_supplier_to_db,
        save_product_to_db,
        query_suppliers_from_db,
        save_trend_to_db,
        query_trends_from_db
    ]
    
    return create_agent(
        model=llm,
        system_prompt=cfg.get("sp"),
        tools=tools,
        checkpointer=get_memory_saver(),
        state_schema=AgentState,
    )
