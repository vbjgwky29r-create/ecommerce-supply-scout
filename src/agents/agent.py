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
from coze_coding_dev_sdk import SearchClient, LLMClient, get_session
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
def image_analysis_tool(image_url: str, analysis_type: str = "general") -> str:
    """
    分析产品图片，识别产品类型、特征、风格等信息，并基于图片内容进行市场分析和货源推荐。
    
    Args:
        image_url: 产品图片URL，可以是网络图片URL或本地图片路径
        analysis_type: 分析类型，可选值：
            - "general": 通用分析（识别产品类型、特征、风格）
            - "product": 产品分析（识别产品细节、材质、功能）
            - "market": 市场分析（基于图片推荐类似产品和市场趋势）
            - "sourcing": 货源分析（基于图片推荐供应商和采购建议）
    
    Returns:
        图片分析结果的JSON格式字符串，包含产品识别、特征分析、市场建议等信息
    """
    try:
        from langchain_core.messages import SystemMessage, HumanMessage
        
        # 创建 context
        ctx = new_context(method="image_analysis")
        
        # 创建 LLM 客户端，使用视觉模型
        llm_client = LLMClient(ctx=ctx)
        
        # 根据分析类型设置不同的提示词
        system_prompts = {
            "general": """你是电商产品视觉分析专家。请详细分析用户上传的产品图片，包括：
1. 产品类型识别（这是什么产品？属于哪个品类？）
2. 产品特征描述（颜色、材质、设计风格、尺寸等）
3. 目标用户群体分析
4. 市场定位判断（高端/中端/平价）
5. 潜在竞争优势和劣势

请以结构化的JSON格式返回分析结果。""",
            
            "product": """你是电商产品细节分析专家。请深入分析用户上传的产品图片，包括：
1. 产品名称和品类
2. 详细规格参数（尺寸、重量、材质等）
3. 产品功能和卖点
4. 包装方式
5. 生产工艺特点
6. 质量评估
7. 预估成本和利润空间

请以结构化的JSON格式返回分析结果。""",
            
            "market": """你是电商市场趋势分析专家。请基于用户上传的产品图片进行市场分析，包括：
1. 产品品类和细分市场
2. 当前市场热度（高/中/低）
3. 目标平台建议（淘宝/拼多多/京东等）
4. 竞争程度评估
5. 市场机会点
6. 价格区间建议
7. 推广渠道建议
8. 热销关键词推荐

请以结构化的JSON格式返回分析结果。""",
            
            "sourcing": """你是电商货源推荐专家。请基于用户上传的产品图片进行货源分析，包括：
1. 产品品类和规格
2. 推荐采购渠道（1688/阿里巴巴/批发市场等）
3. 预估进货价格区间
4. 最小起订量建议
5. 供应商选择要点
6. 质量控制建议
7. 利润率预估
8. 风险提示

请以结构化的JSON格式返回分析结果。"""
        }
        
        system_prompt = system_prompts.get(analysis_type, system_prompts["general"])
        
        # 构建消息
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=[
                {
                    "type": "text",
                    "text": "请详细分析这张产品图片，并按照上述要求返回结构化的JSON格式结果。"
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_url
                    }
                }
            ])
        ]
        
        # 调用视觉模型
        response = llm_client.invoke(
            messages=messages,
            model="doubao-seed-1-6-vision-250815",
            temperature=0.7,
            max_completion_tokens=4096
        )
        
        # 安全地提取响应内容
        def get_text_content(content):
            """安全地从 AIMessage content 中提取文本"""
            if isinstance(content, str):
                return content
            elif isinstance(content, list):
                text_parts = []
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        text_parts.append(item.get("text", ""))
                return " ".join(text_parts)
            else:
                return str(content)
        
        analysis_text = get_text_content(response.content)
        
        # 构建输出结果
        output = {
            "analysis_type": analysis_type,
            "image_url": image_url,
            "analysis_result": analysis_text,
            "model": "doubao-seed-1-6-vision-250815",
            "timestamp": "当前时间"
        }
        
        return json.dumps(output, ensure_ascii=False, indent=2)
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return f"图片分析失败: {str(e)}\n详细信息: {error_details}"

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


def build_agent(ctx=None):
    # 获取当前工作目录（兼容本地和云端部署）
    # 优先使用当前工作目录，而不是环境变量
    workspace_path = os.getcwd()
    
    config_path = os.path.join(workspace_path, LLM_CONFIG)
    
    # 如果配置文件不存在，尝试使用环境变量
    if not os.path.exists(config_path) and os.getenv("COZE_WORKSPACE_PATH"):
        workspace_path = os.getenv("COZE_WORKSPACE_PATH")
        config_path = os.path.join(workspace_path, LLM_CONFIG)
    
    # 如果仍然找不到，抛出清晰的错误
    if not os.path.exists(config_path):
        raise FileNotFoundError(
            f"配置文件未找到: {config_path}\n"
            f"当前工作目录: {os.getcwd()}\n"
            f"COZE_WORKSPACE_PATH: {os.getenv('COZE_WORKSPACE_PATH')}\n"
            f"尝试的路径: {config_path}"
        )
    
    with open(config_path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    
    # 优先使用 ARK_API_KEY（火山方舟的 API Key），如果没有则使用 COZE_WORKLOAD_IDENTITY_API_KEY
    api_key = os.getenv("ARK_API_KEY") or os.getenv("COZE_WORKLOAD_IDENTITY_API_KEY")
    base_url = os.getenv("COZE_INTEGRATION_MODEL_BASE_URL")
    
    # 如果没有找到 API Key，抛出清晰的错误
    if not api_key:
        raise ValueError(
            "缺少必需的环境变量！\n"
            "请配置以下环境变量之一：\n"
            "1. ARK_API_KEY（推荐，用于火山方舟大模型）\n"
            "2. COZE_WORKLOAD_IDENTITY_API_KEY（Coze 平台的工作负载标识符）\n\n"
            "环境变量配置位置：\n"
            "- 本地开发：在 .env 文件中配置\n"
            "- Render 部署：在 Render 控制台的 Environment 标签中配置"
        )
    
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
        image_analysis_tool,
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
        create_trend_notification
    ]
    
    return create_agent(
        model=llm,
        system_prompt=cfg.get("sp"),
        tools=tools,
        checkpointer=get_memory_saver(),
        state_schema=AgentState,
    )
