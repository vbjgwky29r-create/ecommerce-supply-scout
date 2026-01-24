#!/usr/bin/env python
"""
LLM Debug专家团会诊脚本
调用多个LLM作为不同领域的debug专家，深度诊断部署失败的根本原因
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

def expert_diagnosis(expert_role, expert_name, model_id, problem_context):
    """专家诊断"""
    print(f"\n{'='*80}")
    print(f"[{expert_role}] {expert_name} 正在诊断...")
    print(f"{'='*80}\n")

    ctx = new_context(method="debug")
    client = LLMClient(ctx=ctx)

    messages = [
        SystemMessage(content=f"""你是一位资深的{expert_role}专家，专长于诊断和解决复杂的Python部署问题。

请以专业的角度分析问题，并提供：
1. 根本原因分析
2. 验证方法
3. 解决方案（必须可执行）
4. 预防措施

回答要简洁、准确、可操作。"""),
        HumanMessage(content=problem_context)
    ]

    try:
        print("正在深度分析...")
        response = client.invoke(messages=messages, model=model_id, temperature=0.3)
        result = get_text_content(response.content)
        print(result)
        print(f"\n✅ {expert_name} 诊断完成")
        return result
    except Exception as e:
        print(f"❌ {expert_name} 诊断失败: {str(e)}")
        return None

def main():
    """主函数：专家团会诊"""
    print("\n" + "="*80)
    print("🚨 电商货源猎手 - LLM Debug专家团会诊")
    print(f"会诊时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    # 构建问题上下文
    build_log_success = """
【构建成功部分】
#10 59.62 Successfully installed ... coze-coding-dev-sdk-0.5.4 ...
#11 1.093 Version: 0.5.4  # 版本验证通过
"""

    build_log_failure = """
【构建失败部分】
Traceback (most recent call last):
  File "/app/src/web/app.py", line 31, in <module>
    from agents.agent import build_agent
  File "/app/src/web/../agents/agent.py", line 11, in <module>
    from coze_coding_dev_sdk import SearchClient, LLMClient, get_session
  File "/usr/local/lib/python3.11/site-packages/coze_coding_dev_sdk/__init__.py", line 1, in <module>
    from .core import (
  File "/usr/local/lib/python3.11/site-packages/coze_coding_dev_sdk/core/__init__.py", line 1, in <module>
    from .client import BaseClient
  File "/usr/local/lib/python3.11/site-packages/coze_coding_dev_sdk/core/client.py", line 231
    f"响应解析失败: {str(e)}, logid: {response.headers.get("X-Tt-Logid")}, 响应内容: {response.text[:200]}",
                                                      ^
SyntaxError: f-string: unmatched '('
"""

    problem_context = f"""
【问题描述】

这是一个非常矛盾的部署失败现象，需要你深度分析：

{build_log_success}

{build_log_failure}

【关键矛盾点】

1. **requirements.txt 中的版本声明**
   - 文件中明确指定: coze-coding-dev-sdk==0.5.4
   - 已提交到 Git (commit f4b4473)

2. **构建日志显示安装成功**
   - pip 成功安装: coze-coding-dev-sdk-0.5.4
   - 版本验证通过: Version: 0.5.4

3. **但应用启动时仍有 f-string 语法错误**
   - 错误位置: /usr/local/lib/python3.11/site-packages/coze_coding_dev_sdk/core/client.py, line 231
   - 错误信息: f-string: unmatched '('
   - 错误行代码包含双引号嵌套

【核心问题】

既然：
- requirements.txt 指定了 0.5.4 版本
- pip 确实安装了 0.5.4 版本
- 版本验证也通过了

那为什么 0.5.4 版本的 coze_coding_dev_sdk 仍然有 f-string 语法错误？

可能的原因（请分析）：
1. coze-coding-dev-sdk 0.5.4 版本本身就有这个 bug？
2. pip 安装时出现了版本混乱（实际安装了其他版本）？
3. coze-coding-dev-sdk 的发布者发布了错误的 0.5.4 版本？
4. 存在其他依赖强制覆盖了 0.5.4 版本？
5. Render 的构建环境有特殊的缓存或覆盖机制？

【请你作为Python部署debug专家】

1. 分析这个矛盾现象的根本原因
2. 提供验证方法（如何确认实际安装的版本）
3. 提供解决方案（必须可执行）
4. 如果 0.5.4 确实有 bug，是否有其他可用版本？
5. 是否有绕过这个问题的方法？
"""

    # 专家团成员
    experts = [
        {
            "role": "Python依赖管理与包管理专家",
            "name": "包管理专家",
            "model": "doubao-seed-1-6-251015"
        },
        {
            "role": "Python语法与f-string分析专家",
            "name": "语法分析专家",
            "model": "doubao-seed-1-8-251228"
        },
        {
            "role": "Docker与容器化部署专家",
            "name": "容器化专家",
            "model": "deepseek-r1-250528"
        }
    ]

    # 执行会诊
    diagnoses = []
    for expert in experts:
        result = expert_diagnosis(
            expert["role"],
            expert["name"],
            expert["model"],
            problem_context
        )
        diagnoses.append({
            "expert": expert["name"],
            "role": expert["role"],
            "diagnosis": result
        })

    # 生成会诊报告
    print("\n" + "🏥"*40)
    print("Debug专家团会诊报告")
    print("🏥"*40 + "\n")

    report = f"""
# 电商货源猎手 - LLM Debug专家团会诊报告

会诊时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
专家人数: {len(experts)} 位专家

---

## 会诊摘要

| 专家 | 角色 | 状态 |
|-----|------|------|
"""

    for i, expert in enumerate(experts, 1):
        status = "✅ 完成" if diagnoses[i-1]["diagnosis"] else "❌ 失败"
        report += f"| {i}. {expert['name']} | {expert['role']} | {status} |\n"

    report += "\n---\n"

    # 详细诊断
    for i, diagnosis in enumerate(diagnoses, 1):
        report += f"\n## {i}. {diagnosis['expert']} 诊断报告\n\n"
        if diagnosis['diagnosis']:
            report += diagnosis['diagnosis']
        else:
            report += "诊断失败\n"

    # 综合建议
    report += """

---

## 🚨 综合结论与行动方案

请综合以上专家的诊断结果，回答以下问题：

1. **根本原因是什么？**
   - coze-coding-dev-sdk 0.5.4 版本本身有 bug？
   - 还是安装过程出现了问题？

2. **如何验证？**
   - 如何确认实际安装的 coze_coding_dev_sdk 版本？
   - 如何检查 client.py 第 231 行的实际代码？

3. **解决方案有哪些？**
   - 方案 A: 使用其他版本的 coze-coding-dev-sdk
   - 方案 B: 绕过 coze_coding_dev_sdk 的导入
   - 方案 C: 手动修复 client.py 的语法错误
   - 方案 D: 使用私有仓库的修复版本

4. **立即执行的步骤是什么？**
   - 请提供最快速、最可靠的修复步骤

"""

    # 保存报告
    report_path = "scripts/debug_expert_team_report.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n📝 会诊报告已保存到: {report_path}")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
