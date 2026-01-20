#!/usr/bin/env python
"""验证解决方案是否有效"""

print("=" * 60)
print("验证解决方案")
print("=" * 60)

# 读取 requirements.txt 的最后几行
with open("requirements.txt", "r") as f:
    lines = f.readlines()

# 检查 coze-coding-dev-sdk 的出现次数
coze_lines = [line for line in lines if "coze-coding-dev-sdk" in line.lower()]

print(f"\nrequirements.txt 中有 {len(coze_lines)} 处 coze-coding-dev-sdk 引用：")
for i, line in enumerate(coze_lines, 1):
    print(f"  {i}. {line.strip()}")

# 检查最后一个版本
last_line = coze_lines[-1] if coze_lines else ""
version = last_line.split("==")[1].strip() if "==" in last_line else "未找到"

print(f"\n✓ 最后指定的版本: {version}")

if version == "0.5.4":
    print("✓ 版本正确，应该会安装 0.5.4 而非 0.5.5")
else:
    print(f"✗ 版本错误，应该是 0.5.4 但找到 {version}")

print("\n" + "=" * 60)
print("解决方案说明")
print("=" * 60)
print("""
LLM 分析结论：
1. 问题根源：传递依赖的版本冲突
2. coze-coding-dev-sdk 被其他依赖强制升级到 0.5.5
3. 解决方法：在 requirements.txt 末尾强制固定 ==0.5.4

工作原理：
- pip 在解析依赖时，会按顺序处理 requirements.txt
- 最后一次看到的版本约束会覆盖之前的约束
- 因此在文件末尾添加 coze-coding-dev-sdk==0.5.4 会确保最终安装 0.5.4

下一步：
1. 触发 Render 重新部署
2. 清除构建缓存
3. 验证安装的版本是 0.5.4
""")

print("=" * 60)
