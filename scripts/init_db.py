#!/usr/bin/env python3
"""
数据库初始化脚本
创建所有数据库表
"""
import sys
import os

# 设置 PYTHONPATH
workspace_path = os.path.join(os.path.dirname(__file__), '..')
src_path = os.path.join(workspace_path, 'src')
sys.path.insert(0, src_path)
os.environ['PYTHONPATH'] = src_path

from storage.database.db import get_engine
from storage.database.shared.model import Base

def init_database():
    """初始化数据库，创建所有表"""
    try:
        print("开始初始化数据库...")

        # 获取数据库引擎
        engine = get_engine()

        # 创建所有表（如果不存在）
        print("正在创建数据库表...")
        Base.metadata.create_all(bind=engine, checkfirst=True)

        print("✅ 数据库表创建成功！")

        # 列出所有表
        print("\n数据库中的表：")
        from sqlalchemy import inspect
        inspector = inspect(engine)
        for table_name in inspector.get_table_names():
            print(f"  - {table_name}")

        return True

    except Exception as e:
        # 检查错误是否是索引重复（可以忽略）
        if "DuplicateTable" in str(e) or "already exists" in str(e):
            print("⚠️  部分表或索引已存在，跳过创建")

            # 列出所有表
            from sqlalchemy import inspect
            engine = get_engine()
            inspector = inspect(engine)
            print("\n数据库中的表：")
            for table_name in inspector.get_table_names():
                print(f"  - {table_name}")
            return True
        else:
            print(f"❌ 数据库初始化失败: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
