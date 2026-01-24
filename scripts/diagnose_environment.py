#!/usr/bin/env python3
"""
Render 环境诊断脚本

检查环境变量配置是否正确
"""
import os
import sys
import json

def check_environment():
    """检查环境变量配置"""
    print("=" * 80)
    print("Render 环境诊断")
    print("=" * 80)
    
    # 1. 检查必需的环境变量
    required_vars = [
        "COZE_WORKLOAD_IDENTITY_API_KEY",
        "COZE_INTEGRATION_MODEL_BASE_URL",
        "COZE_WORKSPACE_PATH",
    ]
    
    print("\n【1. 必需环境变量检查】")
    print("-" * 80)
    
    all_ok = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            if var == "COZE_WORKLOAD_IDENTITY_API_KEY":
                # 只显示前20个字符
                masked_value = value[:20] + "..." if len(value) > 20 else value
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: 未设置")
            all_ok = False
    
    # 2. 检查配置文件
    print("\n【2. 配置文件检查】")
    print("-" * 80)
    
    workspace_path = os.getenv("COZE_WORKSPACE_PATH", os.getcwd())
    config_path = os.path.join(workspace_path, "config", "agent_llm_config.json")
    
    if os.path.exists(config_path):
        print(f"✅ 配置文件存在: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            print(f"✅ 配置文件可读")
            print(f"\n配置内容:")
            print(json.dumps(config, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"❌ 配置文件读取失败: {e}")
            all_ok = False
    else:
        print(f"❌ 配置文件不存在: {config_path}")
        all_ok = False
    
    # 3. 检查常见错误配置
    print("\n【3. 常见错误配置检查】")
    print("-" * 80)
    
    # 检查是否有 OpenAI 相关的环境变量
    openai_vars = [v for v in os.environ if "OPENAI" in v.upper()]
    if openai_vars:
        print("⚠️  检测到 OpenAI 相关的环境变量:")
        for var in openai_vars:
            value = os.getenv(var)
            masked_value = value[:10] + "..." if value and len(value) > 10 else value
            print(f"   - {var}: {masked_value}")
        print("\n注意: 本应用使用豆包大模型，不需要 OpenAI API key")
    else:
        print("✅ 未检测到 OpenAI 相关的环境变量")
    
    # 4. 检查 Python 环境
    print("\n【4. Python 环境检查】")
    print("-" * 80)
    
    print(f"Python 版本: {sys.version}")
    print(f"Python 路径: {sys.executable}")
    print(f"当前工作目录: {os.getcwd()}")
    print(f"COZE_WORKSPACE_PATH: {workspace_path}")
    
    # 5. 检查关键依赖
    print("\n【5. 关键依赖检查】")
    print("-" * 80)
    
    try:
        import langchain
        print(f"✅ langchain: {langchain.__version__}")
    except ImportError:
        print("❌ langchain 未安装")
        all_ok = False
    
    try:
        import langgraph
        print(f"✅ langgraph: 已安装")
    except ImportError:
        print("❌ langgraph 未安装")
        all_ok = False
    
    try:
        import coze_coding_dev_sdk
        print(f"✅ coze_coding-dev-sdk: {coze_coding_dev_sdk.__version__}")
    except ImportError:
        print("❌ coze-coding-dev-sdk 未安装")
        all_ok = False
    
    try:
        from langchain_openai import ChatOpenAI
        print(f"✅ langchain-openai: 已安装")
    except ImportError:
        print("❌ langchain-openai 未安装")
        all_ok = False
    
    # 6. 诊断结论
    print("\n【诊断结论】")
    print("=" * 80)
    
    if all_ok:
        print("✅ 环境配置正常")
        print("\n如果仍然遇到错误，请检查:")
        print("1. Render 环境变量是否正确设置")
        print("2. Render 部署日志是否有错误信息")
        print("3. 应用是否成功启动")
        return 0
    else:
        print("❌ 环境配置存在问题")
        print("\n请修复以下问题:")
        print("1. 确保所有必需的环境变量都已设置")
        print("2. 确保配置文件存在且可读")
        print("3. 确保所有依赖都已正确安装")
        return 1

if __name__ == "__main__":
    sys.exit(check_environment())
