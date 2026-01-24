#!/usr/bin/env python3
"""
检查所有工具的定义和使用情况
"""

import re
import json

# 读取 agent.py
with open('src/agents/agent.py', 'r', encoding='utf-8') as f:
    agent_code = f.read()

# 1. 提取所有 @tool 装饰器的函数
tool_functions = re.findall(r'@tool\s*\ndef (\w+)\((.*?)\)\s*->\s*str:', agent_code)
print("="*80)
print("1. 工具函数定义检查")
print("="*80)
print(f"找到 {len(tool_functions)} 个工具函数：")
for i, (func_name, params) in enumerate(tool_functions, 1):
    print(f"  {i}. {func_name}({params})")

# 2. 提取 tools 列表中的工具
tools_list_match = re.search(r'tools = \[(.*?)\]', agent_code, re.DOTALL)
if tools_list_match:
    tools_list = tools_list_match.group(1)
    tools_in_list = re.findall(r'(\w+_tool|\w+_notification)', tools_list)
    print("\n" + "="*80)
    print("2. tools 列表中的工具")
    print("="*80)
    print(f"找到 {len(tools_in_list)} 个工具：")
    for i, tool in enumerate(tools_in_list, 1):
        print(f"  {i}. {tool}")

# 3. 对比
print("\n" + "="*80)
print("3. 对比检查")
print("="*80)

defined_tools = set([name for name, _ in tool_functions])
used_tools = set(tools_in_list)

if defined_tools == used_tools:
    print("✅ 所有定义的工具都在 tools 列表中")
    print(f"✅ 工具列表中引用的工具都已定义")
else:
    # 找出缺失的工具
    missing_in_list = defined_tools - used_tools
    missing_definition = used_tools - defined_tools

    if missing_in_list:
        print(f"❌ 定义了但未在列表中的工具 ({len(missing_in_list)}个):")
        for tool in missing_in_list:
            print(f"   - {tool}")

    if missing_definition:
        print(f"❌ 列表中引用但未定义的工具 ({len(missing_definition)}个):")
        for tool in missing_definition:
            print(f"   - {tool}")

# 4. 读取配置文件
print("\n" + "="*80)
print("4. 配置文件中的工具列表")
print("="*80)

try:
    with open('config/agent_llm_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)

    config_tools = config.get('tools', [])
    print(f"配置文件中的工具数量: {len(config_tools)}")

    config_tools_set = set(config_tools)

    # 对比
    if defined_tools == config_tools_set:
        print("✅ 配置文件中的工具与定义一致")
    else:
        missing_in_config = defined_tools - config_tools_set
        extra_in_config = config_tools_set - defined_tools

        if missing_in_config:
            print(f"❌ 定义了但未在配置文件中的工具 ({len(missing_in_config)}个):")
            for tool in missing_in_config:
                print(f"   - {tool}")

        if extra_in_config:
            print(f"❌ 配置文件中存在但未定义的工具 ({len(extra_in_config)}个):")
            for tool in extra_in_config:
                print(f"   - {tool}")

except Exception as e:
    print(f"❌ 读取配置文件失败: {e}")

# 5. 检查工具是否有图片处理相关的问题
print("\n" + "="*80)
print("5. 图片处理工具检查")
print("="*80)

image_related_tools = [
    'image_search_tool',
    'image_analysis_tool'
]

for tool_name in image_related_tools:
    # 提取函数定义
    func_pattern = rf'@tool\s*\ndef {tool_name}\((.*?)\)\s*->\s*str:(.*?)(?=\n@tool|\ndef build_agent|$)'
    match = re.search(func_pattern, agent_code, re.DOTALL)

    if match:
        params, func_body = match.groups()
        print(f"\n工具: {tool_name}")
        print(f"参数: {params}")

        # 检查是否使用了 LLMClient
        if 'LLMClient' in func_body:
            print(f"✅ 使用了 LLMClient")
            # 检查是否处理了 image_url
            if 'image_url' in func_body:
                print(f"✅ 处理了 image_url 参数")
                # 检查是否正确使用了视觉模型
                if 'doubao-seed-1-6-vision' in func_body or 'vision' in func_body.lower():
                    print(f"✅ 使用了视觉模型")
                else:
                    print(f"⚠️  可能未使用视觉模型")
            else:
                print(f"⚠️  未处理 image_url 参数")
        else:
            print(f"⚠️  未使用 LLMClient")

# 6. 检查 URL 路径处理
print("\n" + "="*80)
print("6. URL/路径处理检查")
print("="*80)

# 查找所有使用 os.path.join 或文件路径的地方
path_operations = re.findall(r'os\.path\.join\([^)]+\)|open\([^)]+\)', agent_code)
print(f"找到 {len(path_operations)} 个路径操作")

# 检查是否有将本地路径直接传给 API 的情况
if 'image_url' in agent_code and '/uploads/' in agent_code:
    print(f"⚠️  检测到可能存在本地路径处理问题")
    # 检查是否已经有 base64 转换
    if 'base64' in agent_code and 'base64.b64encode' in agent_code:
        print(f"✅ 已实现 base64 转换")
    else:
        print(f"❌ 未实现 base64 转换")

print("\n" + "="*80)
print("检查完成")
print("="*80)
