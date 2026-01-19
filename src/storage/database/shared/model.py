from coze_coding_dev_sdk.database import Base
from sqlalchemy import BigInteger, Boolean, Column, DateTime, Float, ForeignKey, Index, Integer, String, Text, JSON, func
from sqlalchemy.orm import Mapped, relationship
from typing import Optional
import datetime

class Supplier(Base):
    """供应商表，存储供应商基本信息"""
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="供应商ID")
    name = Column(String(255), nullable=False, index=True, comment="供应商名称")
    company_name = Column(String(255), nullable=True, comment="公司全称")
    contact_person = Column(String(128), nullable=True, comment="联系人")
    contact_phone = Column(String(50), nullable=True, comment="联系电话")
    contact_email = Column(String(255), nullable=True, comment="联系邮箱")
    wechat_id = Column(String(100), nullable=True, comment="微信ID")
    region = Column(String(100), nullable=True, index=True, comment="所在地区")
    address = Column(String(500), nullable=True, comment="详细地址")
    platform = Column(String(50), nullable=True, index=True, comment="主要平台（如1688、阿里巴巴等）")
    platform_url = Column(Text, nullable=True, comment="平台店铺URL")
    min_order_quantity = Column(Integer, nullable=True, comment="最小起订量")
    is_verified = Column(Boolean, default=False, nullable=False, comment="是否为认证供应商")
    rating = Column(Float, nullable=True, comment="评分（0-5分）")
    categories = Column(JSON, nullable=True, comment="经营的品类列表")
    tags = Column(JSON, nullable=True, comment="标签列表")
    notes = Column(Text, nullable=True, comment="备注信息")
    source = Column(String(100), nullable=True, comment="数据来源")
    status = Column(String(50), default="active", nullable=False, index=True, comment="状态：active/inactive")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True, comment="更新时间")

    # 关系
    products = relationship("Product", back_populates="supplier", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_suppliers_platform_region", "platform", "region"),
        Index("ix_suppliers_region_status", "region", "status"),
    )


class Product(Base):
    """产品表，存储产品基本信息"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="产品ID")
    supplier_id = Column(Integer, ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False, index=True, comment="供应商ID")
    name = Column(String(255), nullable=False, index=True, comment="产品名称")
    category = Column(String(100), nullable=True, index=True, comment="产品品类")
    description = Column(Text, nullable=True, comment="产品描述")
    purchase_price = Column(Float, nullable=True, comment="进货价（元）")
    estimated_price = Column(Float, nullable=True, comment="预估销售价（元）")
    logistics_cost = Column(Float, nullable=True, default=0, comment="物流费用（元）")
    min_order_quantity = Column(Integer, nullable=True, comment="最小起订量")
    profit_margin = Column(Float, nullable=True, comment="利润率（%）")
    roi = Column(Float, nullable=True, comment="投资回报率（%）")
    potential_score = Column(Integer, nullable=True, comment="潜力分数（1-10分）")
    image_urls = Column(JSON, nullable=True, comment="产品图片URL列表")
    product_url = Column(Text, nullable=True, comment="产品链接")
    specifications = Column(JSON, nullable=True, comment="规格参数")
    tags = Column(JSON, nullable=True, comment="标签")
    notes = Column(Text, nullable=True, comment="备注")
    status = Column(String(50), default="active", nullable=False, index=True, comment="状态：active/inactive")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True, comment="更新时间")

    # 关系
    supplier = relationship("Supplier", back_populates="products")

    __table_args__ = (
        Index("ix_products_category_status", "category", "status"),
        Index("ix_products_supplier_status", "supplier_id", "status"),
    )


class MarketTrend(Base):
    """市场趋势表，存储市场趋势数据"""
    __tablename__ = "market_trends"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="趋势ID")
    category = Column(String(100), nullable=False, index=True, comment="品类")
    platform = Column(String(50), nullable=True, index=True, comment="平台")
    trend_data = Column(JSON, nullable=True, comment="趋势数据")
    growth_rate = Column(Float, nullable=True, comment="增长率（%）")
    hot_keywords = Column(JSON, nullable=True, comment="热门关键词列表")
    summary = Column(Text, nullable=True, comment="趋势摘要")
    trend_type = Column(String(50), nullable=True, comment="趋势类型：monthly/weekly/daily")
    data_date = Column(DateTime(timezone=True), nullable=True, comment="数据日期")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")

    __table_args__ = (
        Index("ix_market_trends_category_platform", "category", "platform"),
        Index("ix_market_trends_category_date", "category", "data_date"),
    )


class UserPreference(Base):
    """用户偏好表，存储用户的品类和价格偏好"""
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="偏好ID")
    user_id = Column(String(100), nullable=False, index=True, comment="用户ID")
    preferred_categories = Column(JSON, nullable=True, comment="偏好品类列表")
    min_price = Column(Float, nullable=True, comment="最低进货价")
    max_price = Column(Float, nullable=True, comment="最高进货价")
    preferred_platforms = Column(JSON, nullable=True, comment="偏好平台列表")
    preferred_regions = Column(JSON, nullable=True, comment="偏好地区列表")
    min_roi = Column(Float, nullable=True, comment="最低ROI要求（%）")
    min_profit_margin = Column(Float, nullable=True, comment="最低利润率要求（%）")
    keywords = Column(JSON, nullable=True, comment="关注关键词列表")
    exclude_keywords = Column(JSON, nullable=True, comment="排除关键词列表")
    notification_enabled = Column(Boolean, default=True, nullable=False, comment="是否启用通知")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True, comment="更新时间")

    __table_args__ = (
        Index("ix_user_preferences_user_id", "user_id"),
    )


class Notification(Base):
    """通知表，存储系统通知消息"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="通知ID")
    user_id = Column(String(100), nullable=False, index=True, comment="用户ID")
    notification_type = Column(String(50), nullable=False, comment="通知类型：trend_alert/supplier_alert/recommendation")
    title = Column(String(255), nullable=False, comment="通知标题")
    content = Column(Text, nullable=False, comment="通知内容")
    data = Column(JSON, nullable=True, comment="附加数据")
    priority = Column(String(20), default="normal", nullable=False, comment="优先级：low/normal/high/urgent")
    is_read = Column(Boolean, default=False, nullable=False, comment="是否已读")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    read_at = Column(DateTime(timezone=True), nullable=True, comment="阅读时间")

    __table_args__ = (
        Index("ix_notifications_user_id_read", "user_id", "is_read"),
        Index("ix_notifications_user_id_created", "user_id", "created_at"),
    )


class ProductLinkAnalysis(Base):
    """产品链接分析表，存储淘宝/拼多多产品链接的分析结果"""
    __tablename__ = "product_link_analyses"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="分析ID")
    original_url = Column(Text, nullable=False, comment="原始产品链接")
    platform = Column(String(50), nullable=False, index=True, comment="平台：taobao/pinduoduo/jd等")
    product_id = Column(String(100), nullable=True, index=True, comment="平台产品ID")
    product_title = Column(String(500), nullable=True, comment="产品标题")
    category = Column(String(100), nullable=True, index=True, comment="产品品类")
    price = Column(Float, nullable=True, comment="产品价格")
    sales_count = Column(Integer, nullable=True, comment="销量")
    rating = Column(Float, nullable=True, comment="评分")
    review_count = Column(Integer, nullable=True, comment="评价数")
    image_urls = Column(JSON, nullable=True, comment="产品图片URL列表")
    shop_name = Column(String(255), nullable=True, comment="店铺名称")
    shop_url = Column(Text, nullable=True, comment="店铺链接")
    market_analysis = Column(JSON, nullable=True, comment="市场分析数据")
    competitor_info = Column(JSON, nullable=True, comment="竞品信息")
    sourcing_suggestions = Column(JSON, nullable=True, comment="货源建议")
    analysis_summary = Column(Text, nullable=True, comment="分析摘要")
    potential_score = Column(Integer, nullable=True, comment="潜力分数（1-10分）")
    status = Column(String(50), default="analyzed", nullable=False, comment="状态：analyzed/failed/pending")
    error_message = Column(Text, nullable=True, comment="错误信息")
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="分析时间")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")

    __table_args__ = (
        Index("ix_product_link_platform_id", "platform", "product_id"),
        Index("ix_product_link_category_score", "category", "potential_score"),
        Index("ix_product_link_analyzed_at", "analyzed_at"),
    )


class ShopLinkAnalysis(Base):
    """店铺链接分析表，存储淘宝/拼多多店铺链接的分析结果"""
    __tablename__ = "shop_link_analyses"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="分析ID")
    original_url = Column(Text, nullable=False, comment="原始店铺链接")
    platform = Column(String(50), nullable=False, index=True, comment="平台：taobao/pinduoduo/jd等")
    shop_id = Column(String(100), nullable=True, index=True, comment="平台店铺ID")
    shop_name = Column(String(255), nullable=True, comment="店铺名称")
    shop_type = Column(String(50), nullable=True, comment="店铺类型：旗舰店/专营店/个人店")
    shop_rating = Column(Float, nullable=True, comment="店铺评分")
    main_category = Column(String(100), nullable=True, comment="主营品类")
    product_count = Column(Integer, nullable=True, comment="商品数量")
    total_sales = Column(BigInteger, nullable=True, comment="总销量")
    follower_count = Column(Integer, nullable=True, comment="粉丝数")
    founded_date = Column(DateTime(timezone=True), nullable=True, comment="开店时间")
    top_products = Column(JSON, nullable=True, comment="热销产品列表")
    pricing_analysis = Column(JSON, nullable=True, comment="定价分析")
    market_position = Column(JSON, nullable=True, comment="市场定位分析")
    sourcing_opportunities = Column(JSON, nullable=True, comment="货源机会")
    analysis_summary = Column(Text, nullable=True, comment="分析摘要")
    status = Column(String(50), default="analyzed", nullable=False, comment="状态：analyzed/failed/pending")
    error_message = Column(Text, nullable=True, comment="错误信息")
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="分析时间")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")

    __table_args__ = (
        Index("ix_shop_link_platform_id", "platform", "shop_id"),
        Index("ix_shop_link_category_sales", "main_category", "total_sales"),
        Index("ix_shop_link_analyzed_at", "analyzed_at"),
    )

