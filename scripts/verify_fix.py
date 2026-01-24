#!/usr/bin/env python
"""
验证修复后的状态 - 确认 dbus-python 和 PyGObject 已被删除
"""

import subprocess
from pathlib import Path

def check_requirements():
    """检查 requirements.txt"""
    req_file = Path("requirements.txt")
    content = req_file.read_text()

    problematic = ["dbus-python", "PyGObject"]
    issues = [pkg for pkg in problematic if pkg.lower() in content.lower()]

    return issues

def check_git_status():
    """检查 Git 状态"""
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True
    )
    return result.stdout.strip() == ""

def check_latest_commit():
    """检查最新提交"""
    result = subprocess.run(
        ["git", "log", "-1", "--oneline"],
        capture_output=True,
        text=True
    )
    return result.stdout.strip()

def main():
    print("="*60)
    print("验证修复状态")
    print("="*60)

    # 检查 requirements.txt
    issues = check_requirements()
    if issues:
        print(f"❌ requirements.txt 中仍包含问题依赖: {issues}")
        return False
    else:
        print("✅ requirements.txt 中没有 dbus-python 或 PyGObject")

    # 检查 Git 状态
    if check_git_status():
        print("✅ 工作目录干净，没有未提交的更改")
    else:
        print("⚠️  工作目录中有未提交的更改")
        subprocess.run(["git", "status", "--short"])

    # 检查最新提交
    latest_commit = check_latest_commit()
    print(f"✅ 最新提交: {latest_commit}")

    print("\n" + "="*60)
    print("验证通过！代码已准备就绪，等待 Render 部署。")
    print("="*60)

    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
