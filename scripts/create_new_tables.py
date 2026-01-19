#!/usr/bin/env python3
"""
创建新增的数据库表
"""
import sys
import os

# 设置 PYTHONPATH
workspace_path = os.path.join(os.path.dirname(__file__), '..')
src_path = os.path.join(workspace_path, 'src')
sys.path.insert(0, src_path)
os.environ['PYTHONPATH'] = src_path

from sqlalchemy import create_engine, text
from storage.database.db import get_db_url

def create_new_tables():
    """创建新增的数据库表"""
    try:
        print("开始创建新增的数据库表...")
        
        # 获取数据库 URL
        db_url = get_db_url()
        
        # 创建引擎（不使用连接池）
        engine = create_engine(db_url, pool_pre_ping=True)
        
        # 创建表的 SQL 语句
        tables_sql = [
            # user_preferences 表
            """
            CREATE TABLE IF NOT EXISTS user_preferences (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(100) NOT NULL,
                preferred_categories JSONB,
                min_price FLOAT,
                max_price FLOAT,
                preferred_platforms JSONB,
                preferred_regions JSONB,
                min_roi FLOAT,
                min_profit_margin FLOAT,
                keywords JSONB,
                exclude_keywords JSONB,
                notification_enabled BOOLEAN DEFAULT TRUE NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
                updated_at TIMESTAMP WITH TIME ZONE
            )
            """,
            # notifications 表
            """
            CREATE TABLE IF NOT EXISTS notifications (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(100) NOT NULL,
                notification_type VARCHAR(50) NOT NULL,
                title VARCHAR(255) NOT NULL,
                content TEXT NOT NULL,
                data JSONB,
                priority VARCHAR(20) DEFAULT 'normal' NOT NULL,
                is_read BOOLEAN DEFAULT FALSE NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
                read_at TIMESTAMP WITH TIME ZONE
            )
            """,
            # product_link_analyses 表
            """
            CREATE TABLE IF NOT EXISTS product_link_analyses (
                id SERIAL PRIMARY KEY,
                original_url TEXT NOT NULL,
                platform VARCHAR(50) NOT NULL,
                product_id VARCHAR(100),
                product_title VARCHAR(500),
                category VARCHAR(100),
                price FLOAT,
                sales_count INTEGER,
                rating FLOAT,
                review_count INTEGER,
                image_urls JSONB,
                shop_name VARCHAR(255),
                shop_url TEXT,
                market_analysis JSONB,
                competitor_info JSONB,
                sourcing_suggestions JSONB,
                analysis_summary TEXT,
                potential_score INTEGER,
                status VARCHAR(50) DEFAULT 'analyzed' NOT NULL,
                error_message TEXT,
                analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
            )
            """,
            # shop_link_analyses 表
            """
            CREATE TABLE IF NOT EXISTS shop_link_analyses (
                id SERIAL PRIMARY KEY,
                original_url TEXT NOT NULL,
                platform VARCHAR(50) NOT NULL,
                shop_id VARCHAR(100),
                shop_name VARCHAR(255),
                shop_type VARCHAR(50),
                shop_rating FLOAT,
                main_category VARCHAR(100),
                product_count INTEGER,
                total_sales BIGINT,
                follower_count INTEGER,
                founded_date TIMESTAMP WITH TIME ZONE,
                top_products JSONB,
                pricing_analysis JSONB,
                market_position JSONB,
                sourcing_opportunities JSONB,
                analysis_summary TEXT,
                status VARCHAR(50) DEFAULT 'analyzed' NOT NULL,
                error_message TEXT,
                analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
            )
            """
        ]
        
        # 创建索引的 SQL 语句
        indexes_sql = [
            # user_preferences 索引
            "CREATE INDEX IF NOT EXISTS ix_user_preferences_user_id ON user_preferences (user_id)",
            
            # notifications 索引
            "CREATE INDEX IF NOT EXISTS ix_notifications_user_id_read ON notifications (user_id, is_read)",
            "CREATE INDEX IF NOT EXISTS ix_notifications_user_id_created ON notifications (user_id, created_at)",
            
            # product_link_analyses 索引
            "CREATE INDEX IF NOT EXISTS ix_product_link_platform_id ON product_link_analyses (platform, product_id)",
            "CREATE INDEX IF NOT EXISTS ix_product_link_category_score ON product_link_analyses (category, potential_score)",
            "CREATE INDEX IF NOT EXISTS ix_product_link_analyzed_at ON product_link_analyses (analyzed_at)",
            
            # shop_link_analyses 索引
            "CREATE INDEX IF NOT EXISTS ix_shop_link_platform_id ON shop_link_analyses (platform, shop_id)",
            "CREATE INDEX IF NOT EXISTS ix_shop_link_category_sales ON shop_link_analyses (main_category, total_sales)",
            "CREATE INDEX IF NOT EXISTS ix_shop_link_analyzed_at ON shop_link_analyses (analyzed_at)"
        ]
        
        # 执行 SQL
        with engine.begin() as conn:
            # 创建表
            for i, sql in enumerate(tables_sql, 1):
                try:
                    conn.execute(text(sql))
                    print(f"✅ 创建表 {i}/{len(tables_sql)} 成功")
                except Exception as e:
                    print(f"❌ 创建表 {i}/{len(tables_sql)} 失败: {e}")
            
            # 创建索引
            for i, sql in enumerate(indexes_sql, 1):
                try:
                    conn.execute(text(sql))
                    print(f"✅ 创建索引 {i}/{len(indexes_sql)} 成功")
                except Exception as e:
                    print(f"⚠️  创建索引 {i}/{len(indexes_sql)} 失败（可能已存在）: {e}")
        
        print("\n✅ 数据库表创建完成！")
        
        # 列出所有表
        print("\n数据库中的所有表：")
        from sqlalchemy import inspect
        inspector = inspect(engine)
        for table_name in inspector.get_table_names():
            print(f"  - {table_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ 创建数据库表失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_new_tables()
    sys.exit(0 if success else 1)
