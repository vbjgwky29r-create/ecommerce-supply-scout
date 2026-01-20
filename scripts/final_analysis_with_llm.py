#!/usr/bin/env python
"""使用 LLM 彻底分析并解决 Render 部署问题"""

from coze_coding_dev_sdk import LLMClient

# 初始化 LLM 客户端
client = LLMClient()

# 读取当前的 requirements.txt
with open("requirements.txt", "r") as f:
    requirements_content = f.read()

# 提取 coze-coding-dev-sdk 相关行
coze_lines = [line for line in requirements_content.split("\n") if "coze-coding" in line.lower()]

problem_description = f"""
问题背景：
1. 项目部署到 Render 平台（Python 3.11.11）
2. Render 一直在安装 coze-coding-dev-sdk 0.5.5 版本
3. 0.5.5 版本有 f-string 语法错误，导致部署失败
4. requirements.txt 中已经指定 coze-coding-dev-sdk==0.5.4
5. 已删除 dbus-python 依赖
6. Build Command: rm -rf .venv && pip install --no-cache-dir -r requirements.txt

当前 requirements.txt 中的 coze 相关依赖：
{chr(10).join(coze_lines)}

错误信息：
SyntaxError: f-string: unmatched '('
位置：coze_coding_dev_sdk/core/client.py, line 231
问题代码：f"响应解析失败: {{str(e)}}, logid: {{response.headers.get(\"X-Tt-Logid\")}}, 响应内容: {{response.text[:200]}}"

已知问题：
1. 0.5.4 版本没有语法错误
2. 0.5.5 版本有 f-string 语法错误
3. Render 一直安装 0.5.5，忽略 requirements.txt 中的 ==0.5.4 约束

可能的冲突依赖：
- langchain
- langchain-openai
- langgraph
- 其他 lang* 系列包

请分析：
1. 为什么 Render 忽略了 requirements.txt 中的版本约束？
2. 是否有其他依赖强制要求 coze-coding-dev-sdk>=0.5.5？
3. 如何彻底解决这个问题，确保安装 0.5.4 版本？

请提供：
1. 详细的根本原因分析
2. 具体的解决方案代码
3. 验证方法
"""

print("=" * 70)
print("使用 LLM 彻底分析 Render 部署问题")
print("=" * 70)

try:
    response = client.invoke(
        messages=[
            {
                "role": "system",
                "content": "你是一个 Python 依赖管理专家，擅长解决 pip 版本冲突、pip 锁文件、依赖传递等问题。"
            },
            {
                "role": "user",
                "content": problem_description
            }
        ],
        model="doubao-seed-1-6-thinking-250715",
        temperature=0.3,
        thinking="enabled",
        max_completion_tokens=10000
    )

    print("\n" + "=" * 70)
    print("LLM 分析结果")
    print("=" * 70)
    print(response.content)
    print("=" * 70)

except Exception as e:
    print(f"分析失败: {e}")
    import traceback
    traceback.print_exc()
