import os
import sys
import base64
import json

from coze_coding_dev_sdk import LLMClient, get_session
from coze_coding_utils.runtime_ctx.context import new_context
from langchain_core.messages import SystemMessage, HumanMessage

# 读取图片并转换为 base64
image_path = "assets/image.png"

if not os.path.exists(image_path):
    print(f"错误：图片文件不存在: {image_path}")
    sys.exit(1)

# 读取图片并编码为 base64
with open(image_path, "rb") as image_file:
    image_data = base64.b64encode(image_file.read()).decode('utf-8')

# 创建 context
ctx = new_context(method="image_analysis")

# 创建 LLM 客户端
llm_client = LLMClient(ctx=ctx)

# 构建消息
messages = [
    SystemMessage(content="""你是一个专业的 API Key 识别专家。请仔细分析用户上传的图片，识别其中的 API Key。

请特别关注：
1. API Key 的完整内容
2. API Key 的格式（是 UUID 格式还是 Base64 格式）
3. API Key 的长度
4. 这是哪个平台的 API Key（火山方舟、OpenAI、其他）

请直接返回 API Key 的内容，不要添加任何解释。"""),
    HumanMessage(content=[
        {
            "type": "text",
            "text": "请识别图片中的 API Key。"
        },
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{image_data}"
            }
        }
    ])
]

# 调用视觉模型
print("正在分析图片中的 API Key...")
print("-" * 80)

try:
    response = llm_client.invoke(
        messages=messages,
        model="doubao-seed-1-6-vision-250815",
        temperature=0,
        max_completion_tokens=4096
    )
    
    # 提取响应内容
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
    
    print("识别结果：")
    print("=" * 80)
    print(analysis_text)
    print("=" * 80)
    
except Exception as e:
    print(f"错误：{e}")
    import traceback
    traceback.print_exc()
