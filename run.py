#!/usr/bin/env python3
"""
电商货源猎手 - 启动包装器
在应用启动前自动修复依赖版本问题
"""

import os
import sys
import subprocess
import shutil

def find_venv_python():
    """查找虚拟环境中的 Python"""
    # 检查 .venv
    if os.path.exists(".venv/bin/python"):
        return ".venv/bin/python"
    # 检查 /opt/render/project/src/.venv
    if os.path.exists("/opt/render/project/src/.venv/bin/python"):
        return "/opt/render/project/src/.venv/bin/python"
    # 使用系统 Python
    return sys.executable

def check_and_fix_coze_sdk():
    """检查并修复 coze_coding_dev_sdk 版本"""
    venv_python = find_venv_python()

    print(f"=== 启动包装器 ===")
    print(f"使用 Python: {venv_python}")

    # 检查版本
    try:
        result = subprocess.run(
            [venv_python, "-m", "pip", "show", "coze-coding-dev-sdk"],
            capture_output=True,
            text=True,
            check=False
        )

        version_line = [line for line in result.stdout.split('\n') if line.startswith('Version:')]
        if version_line:
            version = version_line[0].split(':')[1].strip()
            print(f"当前版本: {version}")

            if version == "0.5.5":
                print("❌ 发现错误版本 0.5.5，正在修复...")

                # 卸载旧版本
                subprocess.run(
                    [venv_python, "-m", "pip", "uninstall", "-y", "coze-coding-dev-sdk"],
                    capture_output=True,
                    check=False
                )

                # 安装新版本
                result = subprocess.run(
                    [venv_python, "-m", "pip", "install", "--no-cache-dir", "--force-reinstall", "coze-coding-dev-sdk==0.5.4"],
                    capture_output=True,
                    text=True,
                    check=False
                )

                if "Successfully installed coze-coding-dev-sdk" in result.stdout:
                    print("✅ 已修复为版本 0.5.4")
                else:
                    print(f"⚠️ 修复结果: {result.stdout}")
                    print(f"错误: {result.stderr}")
            else:
                print(f"✅ 版本正确: {version}")
        else:
            print("⚠️ 未找到 coze-coding-dev-sdk")
    except Exception as e:
        print(f"⚠️ 版本检查失败: {e}")

def main():
    """主函数"""
    print("=== 电商货源猎手启动器 ===")

    # 修复依赖
    check_and_fix_coze_sdk()

    # 设置 Python 路径
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

    # 导入并启动应用
    try:
        from web.app import app
        print("✅ 应用加载成功")
        app.run(host='0.0.0.0', port=5000, debug=False)
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
