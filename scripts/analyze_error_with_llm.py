#!/usr/bin/env python
"""使用 LLM 分析部署错误"""

from coze_coding_dev_sdk import LLMClient

# 初始化 LLM 客户端
client = LLMClient()

error_log = """
错误信息:
File: /opt/render/project/src/.venv/lib/python3.11/site-packages/coze_coding_dev_sdk/core/client.py, line 231
f"响应解析失败: {str(e)}, logid: {response.headers.get("X-Tt-Logid")}, 响应内容: {response.text[:200]}",

错误类型: SyntaxError: f-string: unmatched '('

上下文:
1. 使用 Python 3.11.11
2. 已指定安装 coze-coding-dev-sdk==0.5.4
3. 已添加 --no-cache-dir 选项
4. 已删除 .venv 目录
5. Render 仍然安装了 0.5.5 版本（有语法错误）

问题:
为什么 Render 一直安装 0.5.5 版本，而不是 requirements-render.txt 中指定的 0.5.4？
"""

print("=" * 60)
print("使用 LLM 分析部署错误")
print("=" * 60)

try:
    response = client.invoke(
        messages=[
            {
                "role": "system",
                "content": "你是一个专业的技术问题分析专家，擅长诊断 Python 部署和依赖管理问题。"
            },
            {
                "role": "user",
                "content": f"请分析以下部署错误，并提供详细的解决方案：\n\n{error_log}"
            }
        ],
        model="doubao-seed-1-6-thinking-250715",
        temperature=0.3,
        thinking="enabled"
    )

    print("\n分析结果：")
    print("-" * 60)
    print(response.content)

except Exception as e:
    print(f"分析失败: {e}")
    import traceback
    traceback.print_exc()
