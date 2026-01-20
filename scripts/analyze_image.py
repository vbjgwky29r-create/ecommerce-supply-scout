#!/usr/bin/env python3
"""
分析 assets/image.png 图片内容
"""

import os
import base64
from coze_coding_dev_sdk import LLMClient
from coze_coding_utils.runtime_ctx.context import Context, new_context
from langchain_core.messages import SystemMessage, HumanMessage

def image_to_base64(image_path):
    """将图片转换为 base64 编码"""
    with open(image_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')

def analyze_image(image_path):
    """分析图片内容"""
    ctx = new_context(method="invoke")

    # 创建客户端
    client = LLMClient(ctx=ctx)

    # 将图片转换为 base64
    image_base64 = image_to_base64(image_path)

    # 构建消息
    messages = [
        SystemMessage(content="你是一个专业的图片分析助手，请详细描述图片的内容，包括识别到的物品、场景、颜色、文字等信息。"),
        HumanMessage(content=[
            {
                "type": "text",
                "text": "请详细分析这张图片，描述你看到的内容。"
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{image_base64}"
                }
            }
        ])
    ]

    print("正在分析图片...")
    print("-" * 60)

    try:
        # 使用视觉模型
        response = client.invoke(
            messages=messages,
            model="doubao-seed-1-6-vision-250815",
            temperature=0.7
        )

        # 安全地提取响应内容
        if isinstance(response.content, str):
            print(response.content)
        elif isinstance(response.content, list):
            for item in response.content:
                if isinstance(item, dict) and item.get("type") == "text":
                    print(item.get("text", ""))
        else:
            print(str(response.content))

        print("-" * 60)
        print(f"\nToken 使用情况: {response.response_metadata.get('usage', {})}")

    except Exception as e:
        print(f"分析失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    image_path = "assets/image.png"

    if not os.path.exists(image_path):
        print(f"错误: 找不到文件 {image_path}")
    else:
        analyze_image(image_path)
