import os
import sys
import json

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import image_analysis_tool

# 读取图片
image_path = "assets/image.png"

if not os.path.exists(image_path):
    print(f"错误：图片文件不存在: {image_path}")
    sys.exit(1)

# 获取图片的绝对路径
abs_image_path = os.path.abspath(image_path)

# 调用图片分析工具
print("正在分析图片中的 API Key...")
print("-" * 80)

try:
    result = image_analysis_tool(
        image_url=abs_image_path,
        analysis_type="general"
    )
    
    print(result)
    
    # 解析结果
    result_dict = json.loads(result)
    print("\n" + "=" * 80)
    print("API Key 识别结果：")
    print("=" * 80)
    
except Exception as e:
    print(f"错误：{e}")
    import traceback
    traceback.print_exc()
