#!/usr/bin/env python
"""
LLM代码审计脚本
实际调用3个不同的LLM模型来审计代码，找出部署失败的根本原因
"""

import os
import sys
import json
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

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

def read_requirements():
    """读取requirements.txt"""
    try:
        with open('requirements.txt', 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading: {str(e)}"

def read_dockerfile():
    """读取Dockerfile"""
    try:
        with open('Dockerfile', 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading: {str(e)}"

def read_agent_py():
    """读取agent.py"""
    try:
        with open('src/agents/agent.py', 'r', encoding='utf-8') as f:
            return f.read()[:2000]  # 只读取前2000字符
    except Exception as e:
        return f"Error reading: {str(e)}"

def audit_with_llm(model_id, model_name, prompt):
    """使用指定LLM进行审计"""
    print(f"\n{'='*80}")
    print(f"[LLM审计] 使用模型: {model_name} ({model_id})")
    print(f"{'='*80}\n")

    ctx = new_context(method="audit")
    client = LLMClient(ctx=ctx)

    messages = [
        SystemMessage(content="你是一位资深的Python开发专家和DevOps工程师，擅长诊断Docker部署问题、依赖冲突和Python包管理。请提供准确、可行的分析和解决方案。"),
        HumanMessage(content=prompt)
    ]

    try:
        print("正在分析...")
        response = client.invoke(messages=messages, model=model_id, temperature=0.3)
        result = get_text_content(response.content)
        print(result)
        print(f"\n✅ {model_name} 审计完成")
        return result
    except Exception as e:
        print(f"❌ {model_name} 审计失败: {str(e)}")
        return None

def main():
    """主函数：调用3个LLM进行审计"""
    print("\n" + "="*80)
    print("电商货源猎手 - LLM代码全面审计")
    print(f"审计时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    # 准备代码上下文
    requirements_txt = read_requirements()
    dockerfile_content = read_dockerfile()
    agent_py_content = read_agent_py()

    # 当前问题
    current_issues = """
【当前问题】
1. Render部署失败，错误信息：
   - coze-coding-dev-sdk 0.5.5版本有f-string语法错误：f-string: unmatched '('
   - 位置：/usr/local/lib/python3.11/site-packages/coze_coding_dev_sdk/core/client.py, line 231

2. 依赖冲突：
   - requirements.txt中包含 dbus-python==1.3.2（需要系统级C库，Docker中编译失败）
   - requirements.txt中包含 PyGObject==3.48.2（需要系统级C库，Docker中编译失败）

3. Docker构建缓存问题：
   - 即使修改了requirements.txt，Docker仍使用缓存的旧版本依赖
   - 已经在Dockerfile添加构建版本号强制清除缓存

4. 之前尝试修复：
   - 多次修改requirements.txt移除问题依赖
   - 使用git提交并推送到GitHub
   - 但构建时仍安装了0.5.5版本和问题依赖
"""

    # LLM 1: 通用模型 - 审计依赖管理问题
    print("\n" + "🔍"*40)
    print("审计 #1/3: 依赖版本冲突问题分析")
    print("🔍"*40)

    prompt_1 = f"""
请分析以下Python项目的依赖管理问题：

【requirements.txt 内容】
{requirements_txt[:500]}

【Dockerfile 内容】
{dockerfile_content}

【问题描述】
{current_issues}

请分析：
1. 为什么本地修改了requirements.txt（将coze-coding-dev-sdk从0.5.5改为0.5.4，移除dbus-python和PyGObject），但Render构建时仍安装了错误的版本？
2. Docker构建缓存机制是如何工作的？为什么添加构建版本号注释不能清除缓存？
3. requirements.txt中是否存在传递依赖导致问题包被重新安装？
4. 提供准确的解决方案，确保Render能使用正确的依赖版本。

请提供具体可执行的修复步骤。
"""

    result1 = audit_with_llm(
        "doubao-seed-1-6-251015",
        "豆包通用模型",
        prompt_1
    )

    # LLM 2: 推理模型 - 深度分析根本原因
    print("\n" + "🧠"*40)
    print("审计 #2/3: 深度推理分析")
    print("🧠"*40)

    prompt_2 = f"""
请进行深度推理分析，找出这个部署问题的根本原因：

【agent.py 导入部分】
{agent_py_content}

【requirements.txt 依赖列表】
{requirements_txt}

【部署错误日志】
```
File "/usr/local/lib/python3.11/site-packages/coze_coding_dev_sdk/core/client.py", line 231
    f"响应解析失败: ..., logid: ..., 响应内容: ...",
                                                      ^
SyntaxError: f-string: unmatched '('
```

【关键矛盾点】
1. requirements.txt本地显示正确版本（0.5.4），但远程构建仍安装0.5.5
2. git log显示提交记录正常，但实际构建使用的是旧依赖
3. Dockerfile添加了版本号注释，但构建日志没有显示重新安装

请深入分析：
1. 是否存在Git工作区/暂存区/本地仓库/远程仓库不同步的问题？
2. 是否存在Render的某些配置覆盖了requirements.txt？
3. pip安装依赖时的解析机制是否存在问题？
4. 是否存在多个requirements.txt文件（如requirements-railway.txt等）被优先使用？

请用逻辑推理找出真正的原因，并提供验证方法。
"""

    result2 = audit_with_llm(
        "doubao-seed-1-6-thinking-250715",
        "豆包推理模型",
        prompt_2
    )

    # LLM 3: 分析模型 - 提供完整解决方案
    print("\n" + "🔧"*40)
    print("审计 #3/3: 完整解决方案")
    print("🔧"*40)

    prompt_3 = f"""
基于前两个模型的审计结果，请提供一个完整、可执行的解决方案：

【项目信息】
- 项目名: 电商货源猎手 (ecommerce-supply-scout)
- 部署平台: Render.com
- Runtime: Docker
- Python版本: 3.11.11
- 依赖管理: pip + requirements.txt

【当前状态】
1. requirements.txt 本地文件状态：请检查是否有问题
2. Git仓库状态：请验证是否正确提交
3. Dockerfile配置：请检查是否有优化空间

【成功标准】
1. coze-coding-dev-sdk版本必须是0.5.4（不是0.5.5）
2. 不安装dbus-python和PyGObject
3. 应用能正常启动，无f-string语法错误
4. 应用能在Render上成功部署并获取公网URL

请提供：
1. 详细的修复步骤（包括命令行操作）
2. 验证步骤（如何确认修复成功）
3. 如果Render仍无法部署，提供备选方案（如其他云平台）
"""

    result3 = audit_with_llm(
        "deepseek-r1-250528",
        "DeepSeek R1分析模型",
        prompt_3
    )

    # 生成综合报告
    print("\n" + "📊"*40)
    print("综合审计报告")
    print("📊"*40 + "\n")

    report = f"""
# 电商货源猎手 - LLM全面审计报告

审计时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
审计模型: 3个（豆包通用、豆包推理、DeepSeek R1）

---

## 审计摘要

### 模型1: 豆包通用模型分析
{'✅ 已完成' if result1 else '❌ 失败'}

### 模型2: 豆包推理模型分析
{'✅ 已完成' if result2 else '❌ 失败'}

### 模型3: DeepSeek R1分析模型
{'✅ 已完成' if result3 else '❌ 失败'}

---

## 详细分析结果

### 1. 依赖版本冲突问题（豆包通用模型）

{result1 if result1 else '审计失败'}

---

### 2. 深度推理分析（豆包推理模型）

{result2 if result2 else '审计失败'}

---

### 3. 完整解决方案（DeepSeek R1模型）

{result3 if result3 else '审计失败'}

---

## 下一步行动

请根据上述分析结果执行修复步骤。
"""

    # 保存报告
    report_path = "scripts/llm_audit_report.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n📝 审计报告已保存到: {report_path}")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
