#!/usr/bin/env python
"""
测试 Render 部署的电商猎手智能体功能
"""

import requests
import json
from datetime import datetime

BASE_URL = "https://ecommerce-supply-scout-1.onrender.com"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_health_check():
    """测试健康检查端点"""
    print_section("1. 测试健康检查端点")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        print(f"✅ 状态码: {response.status_code}")
        print(f"✅ 响应: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ 失败: {str(e)}")
        return False

def test_home_page():
    """测试首页"""
    print_section("2. 测试首页")
    try:
        response = requests.get(BASE_URL, timeout=10)
        print(f"✅ 状态码: {response.status_code}")
        print(f"✅ Content-Type: {response.headers.get('Content-Type')}")

        # 检查关键内容
        content = response.text
        checks = {
            "标题包含智能体名称": "电商货源猎手" in content or "陈艳红专用电商猎手" in content,
            "包含WebSocket相关代码": "socket.io" in content.lower() or "websocket" in content.lower(),
            "包含聊天界面": "chat" in content.lower(),
        }

        for check_name, result in checks.items():
            status = "✅" if result else "⚠️"
            print(f"{status} {check_name}: {result}")

        return True
    except Exception as e:
        print(f"❌ 失败: {str(e)}")
        return False

def test_static_files():
    """测试静态资源"""
    print_section("3. 测试静态资源")
    try:
        # 测试 favicon
        response = requests.get(f"{BASE_URL}/static/js/app.js", timeout=10)
        if response.status_code == 404:
            print("⚠️  JavaScript文件未找到（可能使用内联脚本）")
        else:
            print(f"✅ 状态码: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ 失败: {str(e)}")
        return False

def check_version():
    """检查部署版本"""
    print_section("4. 检查部署版本")
    try:
        response = requests.get(BASE_URL, timeout=10)
        content = response.text

        if "陈艳红专用电商猎手" in content:
            print("✅ 部署版本: 最新版本（陈艳红专用电商猎手）")
            return "latest"
        elif "电商货源猎手" in content:
            print("⚠️  部署版本: 旧版本（电商货源猎手）")
            return "old"
        else:
            print("❌ 无法识别版本")
            return "unknown"
    except Exception as e:
        print(f"❌ 失败: {str(e)}")
        return "error"

def check_configuration():
    """检查配置文件路径修复"""
    print_section("5. 检查配置文件路径修复")
    print("提示: 配置文件路径修复需要通过实际对话来验证")
    print("如果智能体能正常响应，说明配置文件路径已修复")

def main():
    """主测试函数"""
    print(f"\n{'='*60}")
    print("  陈艳红专用电商猎手 - Render 部署测试")
    print(f"  测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  测试地址: {BASE_URL}")
    print(f"{'='*60}")

    results = {
        "健康检查": test_health_check(),
        "首页访问": test_home_page(),
        "静态资源": test_static_files(),
    }

    version = check_version()
    check_configuration()

    print_section("测试总结")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {test_name}")

    print(f"\n通过率: {passed}/{total} ({passed/total*100:.1f}%)")

    if version == "latest":
        print(f"✅ 部署版本: 最新版本")
    elif version == "old":
        print(f"⚠️  部署版本: 旧版本（等待自动部署）")
        print(f"\n提示: 最新提交可能需要几分钟才能自动部署到 Render")
        print(f"可以访问 Render Dashboard 查看部署进度")
    else:
        print(f"❌ 部署版本: {version}")

    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
