#!/usr/bin/env python
"""
构建问题诊断脚本 - 帮助排查 Render 构建失败问题
"""

import subprocess
import json
from pathlib import Path
from datetime import datetime

def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def check_requirements_txt():
    """检查 requirements.txt 中是否包含问题依赖"""
    print_section("📋 检查 requirements.txt")
    
    req_file = Path("requirements.txt")
    
    if not req_file.exists():
        print("❌ requirements.txt 文件不存在！")
        return False
    
    content = req_file.read_text()
    
    problematic_packages = ["dbus-python", "PyGObject"]
    found_issues = []
    
    for pkg in problematic_packages:
        if pkg.lower() in content.lower():
            found_issues.append(pkg)
    
    if found_issues:
        print(f"❌ 发现问题依赖: {', '.join(found_issues)}")
        print("\n问题依赖的行号和内容:")
        for line_num, line in enumerate(content.split('\n'), 1):
            for pkg in found_issues:
                if pkg.lower() in line.lower():
                    print(f"  行 {line_num}: {line}")
        return False
    else:
        print("✅ requirements.txt 中没有发现 dbus-python 或 PyGObject")
        return True

def check_git_status():
    """检查 Git 状态"""
    print_section("🔍 检查 Git 状态")
    
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            output = result.stdout.strip()
            if output:
                print("📝 有未提交的更改:")
                print(output)
            else:
                print("✅ 工作目录干净，没有未提交的更改")
        return True
    except Exception as e:
        print(f"❌ Git 检查失败: {str(e)}")
        return False

def check_git_log():
    """检查最近的提交历史"""
    print_section("📜 检查最近的提交历史")
    
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-5"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            commits = result.stdout.strip().split('\n')
            print("最近5次提交:")
            for commit in commits:
                print(f"  {commit}")
        return True
    except Exception as e:
        print(f"❌ Git log 检查失败: {str(e)}")
        return False

def check_dockerfile():
    """检查 Dockerfile"""
    print_section("🐳 检查 Dockerfile")
    
    dockerfile = Path("Dockerfile")
    
    if not dockerfile.exists():
        print("❌ Dockerfile 文件不存在！")
        return False
    
    content = dockerfile.read_text()
    
    # 检查 BUILD_VERSION
    for line in content.split('\n'):
        if 'ARG BUILD_VERSION=' in line:
            version = line.split('=')[1].strip()
            print(f"✅ BUILD_VERSION: {version}")
            break
    
    # 检查是否移除了不必要的系统依赖
    print("\n系统依赖:")
    for line in content.split('\n'):
        if 'apt-get install' in line or 'RUN apt-get' in line:
            print(f"  {line.strip()}")
    
    return True

def check_config_file():
    """检查配置文件"""
    print_section("⚙️ 检查配置文件")
    
    config_file = Path("config/agent_llm_config.json")
    
    if not config_file.exists():
        print("❌ config/agent_llm_config.json 文件不存在！")
        return False
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("✅ 配置文件存在且格式正确")
        print(f"  模型: {config.get('config', {}).get('model')}")
        print(f"  SP 长度: {len(config.get('sp', ''))} 字符")
        print(f"  工具数量: {len(config.get('tools', []))}")
        
        # 检查是否包含纺织品专家描述
        sp = config.get('sp', '')
        if '纺织品专家' in sp:
            print("  ✅ 包含纺织品专家描述")
        else:
            print("  ⚠️  未包含纺织品专家描述")
        
        return True
    except Exception as e:
        print(f"❌ 配置文件读取失败: {str(e)}")
        return False

def check_transitive_dependencies():
    """检查间接依赖是否可能引入 dbus-python 或 PyGObject"""
    print_section("🔗 检查间接依赖")
    
    # 这些包可能会间接依赖 dbus-python 或 PyGObject
    potentially_problematic = [
        "coze-coding-dev-sdk",
        "coze-coding-utils",
        "cozeloop",
    ]
    
    req_file = Path("requirements.txt")
    if not req_file.exists():
        return False
    
    content = req_file.read_text()
    
    print("检查可能引入问题依赖的包:")
    for pkg in potentially_problematic:
        if pkg in content:
            print(f"  ⚠️  {pkg} - 可能间接引入 dbus-python 或 PyGObject")
        else:
            print(f"  ✅ {pkg} - 未找到")
    
    print("\n💡 建议:")
    print("  如果这些包间接依赖 dbus-python 或 PyGObject，可能需要:")
    print("  1. 降级到不依赖这些包的版本")
    print("  2. 或者在 Dockerfile 中安装额外的系统依赖（不推荐）")
    
    return True

def generate_recommendations():
    """生成修复建议"""
    print_section("💡 修复建议")
    
    print("""
基于当前检查结果，以下是修复建议：

## 立即执行的步骤

1. ✅ 已完成：删除 dbus-python 和 PyGObject
2. ✅ 已完成：更新 BUILD_VERSION 强制重新构建
3. ✅ 已完成：提交并推送代码

## 等待 Render 部署

1. 访问 https://dashboard.render.com
2. 进入 ecommerce-supply-scout-1 服务
3. 查看 Build Log 确认构建是否成功

## 如果仍然失败

### 方案 A: 降级 coze-coding-dev-sdk

尝试将 coze-coding-dev-sdk 降级到 0.5.3 版本:

```bash
# 在 requirements.txt 中修改
coze-coding-dev-sdk==0.5.3

# 然后提交并推送
git add requirements.txt
git commit -m "fix: 降级 coze-coding-dev-sdk 到 0.5.3"
git push origin main
```

### 方案 B: 安装系统依赖（不推荐）

在 Dockerfile 中添加系统依赖:

```dockerfile
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    libpq-dev \\
    libdbus-1-dev \\
    pkg-config \\
    libgirepository-1.0-1 \\
    gobject-introspection \\
    && rm -rf /var/lib/apt/lists/*
```

**注意**: 这会增加镜像大小，且仍可能失败。

### 方案 C: 联系技术支持

如果以上方案都失败，可能需要:
1. 检查 Render 的构建日志获取详细错误
2. 尝试本地 Docker 构建测试
3. 联系技术支持寻求帮助

## 监控部署

使用以下命令监控部署状态:

```bash
python scripts/monitor_render_deployment.py
```

或者访问 Render Dashboard 查看构建日志。
    """)

def main():
    """主函数"""
    print_section("🚀 构建问题诊断工具")
    print(f"  诊断时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  工作目录: {Path.cwd()}")
    
    # 运行所有检查
    results = {
        "requirements.txt": check_requirements_txt(),
        "Git 状态": check_git_status(),
        "Git 历史": check_git_log(),
        "Dockerfile": check_dockerfile(),
        "配置文件": check_config_file(),
        "间接依赖": check_transitive_dependencies(),
    }
    
    # 生成建议
    generate_recommendations()
    
    # 总结
    print_section("📊 诊断总结")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for check_name, result in results.items():
        status = "✅" if result else "❌"
        print(f"{status} {check_name}")
    
    print(f"\n通过率: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 所有检查通过！代码已准备就绪，等待 Render 部署。")
    else:
        print("\n⚠️  发现问题，请根据上述建议进行修复。")

if __name__ == "__main__":
    main()
