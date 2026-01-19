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
from coze_coding_dev_sdk import SearchClient
from storage.memory.memory_saver import get_memory_saver

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
    tools = [web_search_tool, advanced_search_tool]
    
    return create_agent(
        model=llm,
        system_prompt=cfg.get("sp"),
        tools=tools,
        checkpointer=get_memory_saver(),
        state_schema=AgentState,
    )
