#!/usr/bin/env python
"""分析用户上传的图片"""

import os
import sys
from coze_coding_dev_sdk.s3 import S3SyncStorage
from coze_coding_dev_sdk import LLMClient
from coze_coding_utils.runtime_ctx.context import Context
from langchain_core.messages import SystemMessage, HumanMessage

# 初始化对象存储
storage = S3SyncStorage(
    endpoint_url=os.getenv("COZE_BUCKET_ENDPOINT_URL"),
    access_key="",
    secret_key="",
    bucket_name=os.getenv("COZE_BUCKET_NAME"),
    region="cn-beijing",
)

# 初始化 LLM 客户端（不需要 Context 用于简单调用）
client = LLMClient()

# 图片路径
image_path = "assets/image.png"

print("=" * 60)
print("正在分析图片...")
print("=" * 60)

# 1. 读取图片文件
if not os.path.exists(image_path):
    print(f"错误：图片文件不存在 - {image_path}")
    sys.exit(1)

with open(image_path, "rb") as f:
    image_content = f.read()

print(f"✓ 已读取图片文件 ({len(image_content)} 字节)")

# 2. 上传到对象存储
print("正在上传图片到对象存储...")
try:
    key = storage.upload_file(
        file_content=image_content,
        file_name="image.png",
        content_type="image/png",
    )
    print(f"✓ 图片已上传，对象 Key: {key}")
except Exception as e:
    print(f"✗ 上传失败: {e}")
    sys.exit(1)

# 3. 生成签名 URL
print("正在生成访问链接...")
try:
    signed_url = storage.generate_presigned_url(key=key, expire_time=3600)
    print(f"✓ 访问链接: {signed_url}")
except Exception as e:
    print(f"✗ 生成 URL 失败: {e}")
    sys.exit(1)

# 4. 使用视觉模型分析图片
print("\n正在使用视觉模型分析图片内容...")
print("-" * 60)

try:
    messages = [
        SystemMessage(content="你是一个专业的图像分析助手，能够详细、准确地描述和分析图片内容。"),
        HumanMessage(content=[
            {
                "type": "text",
                "text": "请详细描述这张图片的内容，包括：\n1. 图片中的主要对象是什么\n2. 图片的场景和背景\n3. 图片中的文字内容（如果有）\n4. 图片的整体风格和特点\n5. 任何其他值得注意的细节"
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": signed_url
                }
            }
        ])
    ]

    response = client.invoke(
        messages=messages,
        model="doubao-seed-1-6-vision-250815",
        temperature=0.7
    )

    # 安全处理响应内容
    if isinstance(response.content, str):
        result = response.content
    else:
        result = str(response.content)

    print(result)

except Exception as e:
    print(f"✗ 分析失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ 图片分析完成")
print("=" * 60)
