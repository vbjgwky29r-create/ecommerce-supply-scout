"""
Render 部署问题综合诊断
使用多个 LLM 交叉分析部署失败的根本原因
"""

import os
import json
from datetime import datetime

# 收集部署过程中的所有问题和修复尝试
deployment_history = {
    "timestamp": datetime.now().isoformat(),
    "platform": "Render",
    "application": "电商货源猎手 Web 服务",
    "tech_stack": {
        "runtime": "Python 3.11.11",
        "framework": "Flask + Flask-SocketIO",
        "dependencies": "requirements.txt / requirements-render.txt"
    },
    "issues_encountered": [
        {
            "issue": "pandas 编译失败",
            "error": "Python 3.13 与 pandas 2.2.2 不兼容",
            "fix": "创建 .python-version 文件指定 Python 3.11.11"
        },
        {
            "issue": "dbus-python 依赖缺失",
            "error": "Dependency dbus-1 not found",
            "fix": "从 requirements.txt 中移除 dbus-python 和 PyGObject"
        },
        {
            "issue": "找不到 requirements-render.txt",
            "error": "No such file or directory: 'requirements-render.txt'",
            "fix": "创建 requirements-render.txt 文件"
        },
        {
            "issue": "coze_coding_dev_sdk 版本错误（持续问题）",
            "error": "SyntaxError: f-string: unmatched '('",
            "details": "Render 持续安装 0.5.5 版本而不是 0.5.4",
            "attempts": [
                "降级到 0.5.4",
                "重新排序依赖文件（放在第二行）",
                "添加 --force-reinstall 选项",
                "添加 --upgrade 和 --ignore-installed 选项",
                "删除 .venv 缓存目录"
            ]
        },
        {
            "issue": "blinker 模块缺失",
            "error": "ModuleNotFoundError: No module named 'blinker'",
            "fix": "将 blinker==1.9.0 移至 requirements.txt 首行"
        },
        {
            "issue": "端口检测失败",
            "error": "No open ports detected",
            "fix": "修改 app.py 优先使用 Render 的 PORT 环境变量"
        }
    ],
    "current_configuration": {
        "render.yaml": """
services:
  - type: web
    name: ecommerce-scout
    runtime: python
    plan: free
    region: singapore
    buildCommand: rm -rf .venv __pycache__ .pytest_cache && pip install --no-cache-dir --force-reinstall --upgrade --ignore-installed -r requirements-render.txt
    startCommand: python src/web/app.py
""",
        "requirements-render.txt": {
            "first_lines": ["blinker==1.9.0", "coze-coding-dev-sdk==0.5.4", "alembic==1.16.5"],
            "excluded_packages": ["dbus-python", "PyGObject"]
        },
        "app.py": {
            "port_config": "port = int(os.getenv('PORT', os.getenv('WEB_PORT', 5000)))"
        },
        ".python-version": "3.11.11"
    },
    "persistent_problem": {
        "description": "Render 平台持续安装 coze_coding_dev_sdk 0.5.5 版本",
        "error_message": """File "/opt/render/project/src/.venv/lib/python3.11/site-packages/coze_coding_dev_sdk/core/client.py", line 231
    f"响应解析失败: {str(e)}, logid: {response.headers.get("X-Tt-Logid")}, 响应内容: {response.text[:200]}",
                                                      ^
SyntaxError: f-string: unmatched '('""",
        "hypotheses": [
            "Render 平台有多层缓存机制（pip cache、virtualenv cache、repository cache）",
            "coze_coding_dev_sdk 的其他依赖包（coze-coding-utils、cozeloop等）间接引入了 0.5.5 版本",
            "render.yaml 的 buildCommand 在某些情况下被忽略",
            "requirements.txt 和 requirements-render.txt 同时存在导致冲突",
            "pip 的依赖解析器选择了更高版本的 coze_coding_dev_sdk"
        ]
    }
}

# 保存诊断报告
os.makedirs("scripts", exist_ok=True)
with open("scripts/deployment_diagnosis_report.json", "w", encoding="utf-8") as f:
    json.dump(deployment_history, f, ensure_ascii=False, indent=2)

print("部署诊断报告已保存到 scripts/deployment_diagnosis_report.json")
print("\n=== 需要分析的关键问题 ===")
for issue in deployment_history["issues_encountered"]:
    print(f"\n问题: {issue['issue']}")
    print(f"错误: {issue.get('error', 'N/A')}")
    if "attempts" in issue:
        print(f"尝试次数: {len(issue['attempts'])}")

print("\n=== 持久化问题 ===")
print(deployment_history["persistent_problem"]["description"])
print("\n假设:")
for i, hypothesis in enumerate(deployment_history["persistent_problem"]["hypotheses"], 1):
    print(f"{i}. {hypothesis}")
