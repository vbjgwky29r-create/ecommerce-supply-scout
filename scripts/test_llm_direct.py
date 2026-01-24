#!/usr/bin/env python
"""
直接测试LLM API调用
"""

from coze_coding_utils.runtime_ctx.context import new_context
from coze_coding_dev_sdk import LLMClient
from langchain_core.messages import SystemMessage, HumanMessage

def get_text_content(content):
    """安全提取文本内容"""
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        if content and isinstance(content[0], str):
            return " ".join(content)
        else:
            return " ".join(item.get("text", "") for item in content if isinstance(item, dict) and item.get("type") == "text")
    return str(content)

print("="*80)
print("测试 LLM API 直接调用")
print("="*80)

ctx = new_context(method="test")
client = LLMClient(ctx=ctx)

messages = [
    SystemMessage(content="你是一个简洁的助手，用不超过50个字回答。"),
    HumanMessage(content="1+1等于几？")
]

try:
    print("\n正在调用 LLM...")
    response = client.invoke(messages=messages, model="doubao-seed-1-6-251015", temperature=0.3)
    result = get_text_content(response.content)
    print(f"\n✅ LLM 响应: {result}")
    print(f"\n响应长度: {len(result)} 字符")
    print(f"\n响应元数据: {response.response_metadata}")
    print("\n" + "="*80)
    print("✅ LLM API 调用成功！")
    print("="*80)
except Exception as e:
    print(f"\n❌ LLM API 调用失败: {str(e)}")
    print("="*80)
