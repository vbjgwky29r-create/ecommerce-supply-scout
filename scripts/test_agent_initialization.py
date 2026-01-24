#!/usr/bin/env python
"""
测试 Agent 初始化 - 验证配置文件路径和 SDK 导入
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def test_environment():
    """测试环境变量和路径"""
    print_section("🌍 测试环境")

    print(f"当前工作目录: {os.getcwd()}")
    print(f"项目根目录: {project_root}")
    print(f"COZE_WORKSPACE_PATH: {os.getenv('COZE_WORKSPACE_PATH', '未设置')}")

def test_config_file():
    """测试配置文件"""
    print_section("📋 测试配置文件")

    config_path = Path("config/agent_llm_config.json")

    if not config_path.is_absolute():
        config_path = project_root / config_path

    print(f"配置文件路径: {config_path}")

    if config_path.exists():
        print(f"✅ 配置文件存在")
        print(f"   文件大小: {config_path.stat().st_size} 字节")

        import json
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        print(f"   模型: {config.get('config', {}).get('model')}")
        print(f"   SP 长度: {len(config.get('sp', ''))} 字符")
        print(f"   工具数量: {len(config.get('tools', []))}")
        return True
    else:
        print(f"❌ 配置文件不存在")
        return False

def test_sdk_import():
    """测试 SDK 导入"""
    print_section("📦 测试 SDK 导入")

    try:
        import coze_coding_dev_sdk
        print(f"✅ coze_coding_dev_sdk 导入成功")

        # 检查版本
        import subprocess
        result = subprocess.run(
            ["pip", "show", "coze-coding-dev-sdk"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if line.startswith('Version:'):
                    version = line.split(':')[1].strip()
                    print(f"   版本: {version}")
                    if version == "0.5.3":
                        print(f"   ✅ 版本正确（应该是 0.5.3）")
                    else:
                        print(f"   ⚠️  版本可能不正确（应该是 0.5.3）")
                    break
        return True
    except ImportError as e:
        print(f"❌ SDK 导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 检查 SDK 版本时出错: {e}")
        return False

def test_agent_build():
    """测试 Agent 构建"""
    print_section("🤖 测试 Agent 构建")

    try:
        from agents.agent import build_agent

        print("✅ 成功导入 build_agent 函数")
        print("⏳ 正在构建 Agent...")

        agent = build_agent()

        print("✅ Agent 构建成功")
        print(f"   Agent 类型: {type(agent)}")
        return True
    except FileNotFoundError as e:
        print(f"❌ 配置文件错误: {e}")
        print(f"\n💡 请检查：")
        print(f"   1. config/agent_llm_config.json 是否存在")
        print(f"   2. 文件路径是否正确")
        print(f"   3. 工作目录是否正确")
        return False
    except SyntaxError as e:
        print(f"❌ SDK 语法错误: {e}")
        print(f"\n💡 这通常是因为 coze-coding-dev-sdk 版本问题")
        print(f"   请确保使用版本 0.5.3")
        return False
    except Exception as e:
        print(f"❌ Agent 构建失败: {e}")
        print(f"\n错误类型: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print_section("🚀 Agent 初始化测试")
    print(f"  测试时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = {
        "环境检查": test_environment(),
        "配置文件": test_config_file(),
        "SDK 导入": test_sdk_import(),
        "Agent 构建": test_agent_build(),
    }

    print_section("📊 测试总结")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")

    print(f"\n通过率: {passed}/{total} ({passed/total*100:.1f}%)")

    if passed == total:
        print("\n🎉 所有测试通过！Agent 可以正常初始化。")
        return 0
    else:
        print("\n⚠️  发现问题，请根据上述错误信息进行修复。")
        return 1

if __name__ == "__main__":
    exit(main())
