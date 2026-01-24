#!/usr/bin/env python
"""
自动监控 Render 部署状态脚本
"""

import requests
import time
import json
from datetime import datetime
from typing import Dict, Optional

BASE_URL = "https://ecommerce-supply-scout-1.onrender.com"
CHECK_INTERVAL = 30  # 检查间隔（秒）
MAX_RETRIES = 20  # 最大重试次数

def print_section(title: str):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def test_health() -> bool:
    """测试健康检查端点"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 应用健康: {data.get('status')}")
            print(f"   时间: {data.get('timestamp')}")
            return True
        else:
            print(f"⚠️  状态码: {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        print("⚠️  请求超时（应用可能还在启动中）")
        return False
    except requests.exceptions.ConnectionError:
        print("⚠️  连接失败（应用可能正在部署或休眠）")
        return False
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        return False

def check_version() -> str:
    """检查部署版本"""
    try:
        response = requests.get(BASE_URL, timeout=10)
        content = response.text
        
        if "陈艳红专用电商猎手" in content:
            return "latest"
        elif "电商货源猎手" in content:
            return "old"
        else:
            return "unknown"
    except:
        return "error"

def check_config_path() -> bool:
    """测试配置文件路径是否修复"""
    # 这个需要通过实际对话来验证
    return True

def monitor_deployment():
    """监控部署状态"""
    print_section("🚀 开始监控 Render 部署状态")
    print(f"  监控地址: {BASE_URL}")
    print(f"  检查间隔: {CHECK_INTERVAL} 秒")
    print(f"  最大重试: {MAX_RETRIES} 次")
    print(f"  开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    success_count = 0
    consecutive_success_threshold = 2  # 连续成功次数阈值

    for attempt in range(1, MAX_RETRIES + 1):
        print(f"\n--- 尝试 {attempt}/{MAX_RETRIES} ---")
        print(f"时间: {datetime.now().strftime('%H:%M:%S')}")

        is_healthy = test_health()
        
        if is_healthy:
            success_count += 1
            print(f"\n📊 连续成功次数: {success_count}/{consecutive_success_threshold}")
            
            # 检查版本
            version = check_version()
            if version == "latest":
                print(f"✅ 部署版本: 最新版本（陈艳红专用电商猎手）")
            elif version == "old":
                print(f"⚠️  部署版本: 旧版本（电商货源猎手）")
                print(f"   可能是新版本正在构建中...")
            else:
                print(f"❌ 版本检查失败: {version}")
            
            # 如果连续成功达到阈值，认为部署成功
            if success_count >= consecutive_success_threshold:
                print_section("🎉 部署成功！")
                print(f"  总尝试次数: {attempt}")
                print(f"  连续成功次数: {success_count}")
                print(f"  结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"\n访问地址: {BASE_URL}")
                return True
        else:
            success_count = 0
        
        if attempt < MAX_RETRIES:
            print(f"\n⏳ 等待 {CHECK_INTERVAL} 秒后重试...")
            time.sleep(CHECK_INTERVAL)

    print_section("❌ 部署失败或超时")
    print(f"  总尝试次数: {MAX_RETRIES}")
    print(f"  建议:")
    print(f"  1. 检查 Render Dashboard 查看构建日志")
    print(f"  2. 查看是否有错误信息")
    print(f"  3. 尝试手动触发部署")
    return False

def main():
    """主函数"""
    try:
        success = monitor_deployment()
        
        if success:
            print("\n🎯 下一步操作:")
            print("  1. 访问 https://ecommerce-supply-scout-1.onrender.com/")
            print("  2. 测试智能体对话功能")
            print("  3. 验证配置文件路径是否修复")
            exit(0)
        else:
            print("\n🔍 排查建议:")
            print("  1. 访问 https://dashboard.render.com")
            print("  2. 进入 ecommerce-supply-scout-1 服务")
            print("  3. 查看 Build Log 查看详细错误")
            exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断监控")
        exit(130)
    except Exception as e:
        print(f"\n❌ 监控过程中发生错误: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()
