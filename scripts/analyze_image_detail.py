import os
import sys
import base64
from coze_coding_dev_sdk import LLMClient
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

# 构建消息 - 这次更详细地分析图片内容
messages = [
    SystemMessage(content="""你是一个专业的界面识别专家。请仔细分析用户上传的火山方舟控制台截图。

请特别关注：
1. 页面的标题和导航栏信息
2. 所有可见的文本内容
3. API Key 相关的所有字段和标签
4. 是否有"API Key"、"密钥"、"Access Key"等字样
5. 是否有"Service ID"、"应用ID"、"接入点ID"等字样
6. 页面中是否有多个不同的 ID 或 Key

请详细描述图片中的所有内容，不要遗漏任何细节。"""),
    HumanMessage(content=[
        {
            "type": "text",
            "text": "请详细描述图片中的所有内容，特别是与 API Key 相关的部分。"
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
print("正在详细分析火山方舟控制台截图...")
print("=" * 80)

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
    
    print("详细分析结果：")
    print("=" * 80)
    print(analysis_text)
    print("=" * 80)
    
except Exception as e:
    print(f"错误：{e}")
    import traceback
    traceback.print_exc()
