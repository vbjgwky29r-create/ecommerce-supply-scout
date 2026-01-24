import os
import sys
import base64
from langchain_openai import ChatOpenAI

# 读取图片并转换为 base64
image_path = "assets/image.png"

if not os.path.exists(image_path):
    print(f"错误：图片文件不存在: {image_path}")
    sys.exit(1)

# 读取图片并编码为 base64
with open(image_path, "rb") as image_file:
    image_data = base64.b64encode(image_file.read()).decode('utf-8')

# 创建视觉模型
api_key = os.getenv("COZE_WORKLOAD_IDENTITY_API_KEY")
base_url = os.getenv("COZE_INTEGRATION_MODEL_BASE_URL", "https://integration.coze.cn/api/v3")

llm = ChatOpenAI(
    model="doubao-seed-1-6-vision-250815",
    api_key=api_key,
    base_url=base_url,
    temperature=0,
)

# 构建消息（使用正确的格式）
from langchain_core.messages import HumanMessage, SystemMessage

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

# 调用模型
try:
    response = llm.invoke(messages)
    print("识别结果：")
    print(response.content)
except Exception as e:
    print(f"错误：{e}")
    import traceback
    traceback.print_exc()
