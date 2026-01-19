"""
供应商数据库管理器
提供供应商相关的CRUD操作
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from datetime import datetime
import json

from storage.database.shared.model import Supplier, Product, MarketTrend, UserPreference, Notification


# --- Pydantic Models ---
class SupplierCreate(BaseModel):
    """创建供应商的模型"""
    name: str = Field(..., description="供应商名称")
    company_name: Optional[str] = Field(None, description="公司全称")
    contact_person: Optional[str] = Field(None, description="联系人")
    contact_phone: Optional[str] = Field(None, description="联系电话")
    contact_email: Optional[str] = Field(None, description="联系邮箱")
    wechat_id: Optional[str] = Field(None, description="微信ID")
    region: Optional[str] = Field(None, description="所在地区")
    address: Optional[str] = Field(None, description="详细地址")
    platform: Optional[str] = Field(None, description="主要平台")
    platform_url: Optional[str] = Field(None, description="平台店铺URL")
    min_order_quantity: Optional[int] = Field(None, description="最小起订量")
    is_verified: Optional[bool] = Field(False, description="是否为认证供应商")
    rating: Optional[float] = Field(None, ge=0, le=5, description="评分")
    categories: Optional[List[str]] = Field(None, description="经营的品类列表")
    tags: Optional[List[str]] = Field(None, description="标签列表")
    notes: Optional[str] = Field(None, description="备注信息")
    source: Optional[str] = Field(None, description="数据来源")


class SupplierUpdate(BaseModel):
    """更新供应商的模型"""
    name: Optional[str] = None
    company_name: Optional[str] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    wechat_id: Optional[str] = None
    region: Optional[str] = None
    address: Optional[str] = None
    platform: Optional[str] = None
    platform_url: Optional[str] = None
    min_order_quantity: Optional[int] = None
    is_verified: Optional[bool] = None
    rating: Optional[float] = None
    categories: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    status: Optional[str] = None


class ProductCreate(BaseModel):
    """创建产品的模型"""
    supplier_id: int = Field(..., description="供应商ID")
    name: str = Field(..., description="产品名称")
    category: Optional[str] = Field(None, description="产品品类")
    description: Optional[str] = Field(None, description="产品描述")
    purchase_price: Optional[float] = Field(None, ge=0, description="进货价")
    estimated_price: Optional[float] = Field(None, ge=0, description="预估销售价")
    logistics_cost: Optional[float] = Field(0, ge=0, description="物流费用")
    min_order_quantity: Optional[int] = Field(None, ge=1, description="最小起订量")
    potential_score: Optional[int] = Field(None, ge=1, le=10, description="潜力分数")
    image_urls: Optional[List[str]] = Field(None, description="产品图片URL列表")
    product_url: Optional[str] = Field(None, description="产品链接")
    specifications: Optional[Dict[str, Any]] = Field(None, description="规格参数")
    tags: Optional[List[str]] = Field(None, description="标签")
    notes: Optional[str] = Field(None, description="备注")


class ProductUpdate(BaseModel):
    """更新产品的模型"""
    name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    purchase_price: Optional[float] = None
    estimated_price: Optional[float] = None
    logistics_cost: Optional[float] = None
    min_order_quantity: Optional[int] = None
    profit_margin: Optional[float] = None
    roi: Optional[float] = None
    potential_score: Optional[int] = None
    image_urls: Optional[List[str]] = None
    product_url: Optional[str] = None
    specifications: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    status: Optional[str] = None


class MarketTrendCreate(BaseModel):
    """创建市场趋势的模型"""
    category: str = Field(..., description="品类")
    platform: Optional[str] = Field(None, description="平台")
    trend_data: Optional[Dict[str, Any]] = Field(None, description="趋势数据")
    growth_rate: Optional[float] = Field(None, description="增长率（%）")
    hot_keywords: Optional[List[str]] = Field(None, description="热门关键词列表")
    summary: Optional[str] = Field(None, description="趋势摘要")
    trend_type: Optional[str] = Field("monthly", description="趋势类型")
    data_date: Optional[datetime] = Field(None, description="数据日期")


# --- Manager Class ---
class SupplierManager:
    """供应商管理器，处理供应商、产品和市场趋势的CRUD操作"""

    # ========== Supplier Operations ==========
    def create_supplier(self, db: Session, supplier_in: SupplierCreate) -> Supplier:
        """创建新供应商"""
        supplier_data = supplier_in.model_dump(exclude_none=True)
        # 处理JSON字段
        if supplier_data.get('categories'):
            supplier_data['categories'] = json.dumps(supplier_data['categories'], ensure_ascii=False)
        if supplier_data.get('tags'):
            supplier_data['tags'] = json.dumps(supplier_data['tags'], ensure_ascii=False)

        db_supplier = Supplier(**supplier_data)
        db.add(db_supplier)
        try:
            db.commit()
            db.refresh(db_supplier)
            return db_supplier
        except Exception as e:
            db.rollback()
            raise

    def get_suppliers(self, db: Session, skip: int = 0, limit: int = 100, **filters) -> List[Supplier]:
        """获取供应商列表，支持过滤"""
        query = db.query(Supplier)
        for attr, value in filters.items():
            if hasattr(Supplier, attr):
                query = query.filter(getattr(Supplier, attr) == value)
        return query.order_by(Supplier.created_at.desc()).offset(skip).limit(limit).all()

    def get_supplier_by_id(self, db: Session, supplier_id: int) -> Optional[Supplier]:
        """根据ID获取供应商"""
        return db.query(Supplier).filter(Supplier.id == supplier_id).first()

    def search_suppliers(self, db: Session, category: Optional[str] = None,
                         region: Optional[str] = None, platform: Optional[str] = None,
                         min_price: Optional[float] = None, max_price: Optional[float] = None,
                         skip: int = 0, limit: int = 100) -> List[Supplier]:
        """搜索供应商，支持多条件查询"""
        query = db.query(Supplier)

        if category:
            # 搜索包含该品类的供应商
            query = query.filter(Supplier.categories.op('->>')('0').contains(category))
        if region:
            query = query.filter(Supplier.region == region)
        if platform:
            query = query.filter(Supplier.platform == platform)
        if min_price is not None or max_price is not None:
            # 需要关联产品表
            query = query.join(Product).filter(Product.status == 'active')
            if min_price:
                query = query.filter(Product.purchase_price >= min_price)
            if max_price:
                query = query.filter(Product.purchase_price <= max_price)

        return query.distinct().order_by(Supplier.created_at.desc()).offset(skip).limit(limit).all()

    def update_supplier(self, db: Session, supplier_id: int, supplier_in: SupplierUpdate) -> Optional[Supplier]:
        """更新供应商信息"""
        db_supplier = self.get_supplier_by_id(db, supplier_id)
        if not db_supplier:
            return None

        update_data = supplier_in.model_dump(exclude_none=True, exclude_unset=True)
        # 处理JSON字段
        if 'categories' in update_data:
            update_data['categories'] = json.dumps(update_data['categories'], ensure_ascii=False)
        if 'tags' in update_data:
            update_data['tags'] = json.dumps(update_data['tags'], ensure_ascii=False)

        for field, value in update_data.items():
            if hasattr(db_supplier, field):
                setattr(db_supplier, field, value)

        db.add(db_supplier)
        try:
            db.commit()
            db.refresh(db_supplier)
            return db_supplier
        except Exception as e:
            db.rollback()
            raise

    def delete_supplier(self, db: Session, supplier_id: int) -> bool:
        """删除供应商"""
        db_supplier = self.get_supplier_by_id(db, supplier_id)
        if not db_supplier:
            return False
        db.delete(db_supplier)
        db.commit()
        return True

    # ========== Product Operations ==========
    def create_product(self, db: Session, product_in: ProductCreate) -> Product:
        """创建新产品"""
        product_data = product_in.model_dump(exclude_none=True)
        # 计算利润率和ROI
        if product_data.get('purchase_price') and product_data.get('estimated_price'):
            purchase_price = product_data['purchase_price']
            estimated_price = product_data['estimated_price']
            logistics_cost = product_data.get('logistics_cost', 0)
            
            total_cost = purchase_price + logistics_cost
            profit = estimated_price - total_cost
            product_data['profit_margin'] = (profit / total_cost * 100) if total_cost > 0 else 0
            product_data['roi'] = (profit / total_cost * 100) if total_cost > 0 else 0

        # 处理JSON字段
        if product_data.get('image_urls'):
            product_data['image_urls'] = json.dumps(product_data['image_urls'], ensure_ascii=False)
        if product_data.get('specifications'):
            product_data['specifications'] = json.dumps(product_data['specifications'], ensure_ascii=False)
        if product_data.get('tags'):
            product_data['tags'] = json.dumps(product_data['tags'], ensure_ascii=False)

        db_product = Product(**product_data)
        db.add(db_product)
        try:
            db.commit()
            db.refresh(db_product)
            return db_product
        except Exception as e:
            db.rollback()
            raise

    def get_products(self, db: Session, skip: int = 0, limit: int = 100, **filters) -> List[Product]:
        """获取产品列表，支持过滤"""
        query = db.query(Product)
        for attr, value in filters.items():
            if hasattr(Product, attr):
                query = query.filter(getattr(Product, attr) == value)
        return query.order_by(Product.created_at.desc()).offset(skip).limit(limit).all()

    def get_product_by_id(self, db: Session, product_id: int) -> Optional[Product]:
        """根据ID获取产品"""
        return db.query(Product).filter(Product.id == product_id).first()

    def get_products_by_supplier(self, db: Session, supplier_id: int,
                                  skip: int = 0, limit: int = 100) -> List[Product]:
        """获取指定供应商的产品列表"""
        return db.query(Product).filter(
            Product.supplier_id == supplier_id,
            Product.status == 'active'
        ).order_by(Product.created_at.desc()).offset(skip).limit(limit).all()

    def search_products(self, db: Session, category: Optional[str] = None,
                        min_price: Optional[float] = None, max_price: Optional[float] = None,
                        min_potential_score: Optional[int] = None,
                        skip: int = 0, limit: int = 100) -> List[Product]:
        """搜索产品，支持多条件查询"""
        query = db.query(Product).filter(Product.status == 'active')

        if category:
            query = query.filter(Product.category == category)
        if min_price:
            query = query.filter(Product.purchase_price >= min_price)
        if max_price:
            query = query.filter(Product.purchase_price <= max_price)
        if min_potential_score:
            query = query.filter(Product.potential_score >= min_potential_score)

        return query.order_by(Product.potential_score.desc()).offset(skip).limit(limit).all()

    def update_product(self, db: Session, product_id: int, product_in: ProductUpdate) -> Optional[Product]:
        """更新产品信息"""
        db_product = self.get_product_by_id(db, product_id)
        if not db_product:
            return None

        update_data = product_in.model_dump(exclude_none=True, exclude_unset=True)
        
        # 重新计算利润率和ROI
        if 'purchase_price' in update_data or 'estimated_price' in update_data or 'logistics_cost' in update_data:
            purchase_price = update_data.get('purchase_price', db_product.purchase_price) or 0
            estimated_price = update_data.get('estimated_price', db_product.estimated_price) or 0
            logistics_cost = update_data.get('logistics_cost', db_product.logistics_cost) or 0
            
            if purchase_price and estimated_price:
                total_cost = purchase_price + logistics_cost
                profit = estimated_price - total_cost
                update_data['profit_margin'] = (profit / total_cost * 100) if total_cost > 0 else 0
                update_data['roi'] = (profit / total_cost * 100) if total_cost > 0 else 0

        # 处理JSON字段
        if 'image_urls' in update_data:
            update_data['image_urls'] = json.dumps(update_data['image_urls'], ensure_ascii=False)
        if 'specifications' in update_data:
            update_data['specifications'] = json.dumps(update_data['specifications'], ensure_ascii=False)
        if 'tags' in update_data:
            update_data['tags'] = json.dumps(update_data['tags'], ensure_ascii=False)

        for field, value in update_data.items():
            if hasattr(db_product, field):
                setattr(db_product, field, value)

        db.add(db_product)
        try:
            db.commit()
            db.refresh(db_product)
            return db_product
        except Exception as e:
            db.rollback()
            raise

    def delete_product(self, db: Session, product_id: int) -> bool:
        """删除产品"""
        db_product = self.get_product_by_id(db, product_id)
        if not db_product:
            return False
        db.delete(db_product)
        db.commit()
        return True

    # ========== Market Trend Operations ==========
    def create_market_trend(self, db: Session, trend_in: MarketTrendCreate) -> MarketTrend:
        """创建市场趋势记录"""
        trend_data = trend_in.model_dump(exclude_none=True)
        
        # 处理JSON字段
        if trend_data.get('trend_data'):
            trend_data['trend_data'] = json.dumps(trend_data['trend_data'], ensure_ascii=False)
        if trend_data.get('hot_keywords'):
            trend_data['hot_keywords'] = json.dumps(trend_data['hot_keywords'], ensure_ascii=False)

        db_trend = MarketTrend(**trend_data)
        db.add(db_trend)
        try:
            db.commit()
            db.refresh(db_trend)
            return db_trend
        except Exception as e:
            db.rollback()
            raise

    def get_market_trends(self, db: Session, category: Optional[str] = None,
                          platform: Optional[str] = None,
                          skip: int = 0, limit: int = 100) -> List[MarketTrend]:
        """获取市场趋势列表"""
        query = db.query(MarketTrend)
        if category:
            query = query.filter(MarketTrend.category == category)
        if platform:
            query = query.filter(MarketTrend.platform == platform)
        return query.order_by(MarketTrend.data_date.desc()).offset(skip).limit(limit).all()

    def get_latest_trend(self, db: Session, category: str,
                         platform: Optional[str] = None) -> Optional[MarketTrend]:
        """获取最新的趋势记录"""
        query = db.query(MarketTrend).filter(MarketTrend.category == category)
        if platform:
            query = query.filter(MarketTrend.platform == platform)
        return query.order_by(MarketTrend.data_date.desc()).first()

    def delete_market_trend(self, db: Session, trend_id: int) -> bool:
        """删除市场趋势记录"""
        db_trend = db.query(MarketTrend).filter(MarketTrend.id == trend_id).first()
        if not db_trend:
            return False
        db.delete(db_trend)
        db.commit()
        return True

    # ========== User Preference Operations ==========
    def get_user_preference(self, db: Session, user_id: str) -> Optional[UserPreference]:
        """获取用户偏好设置"""
        return db.query(UserPreference).filter(UserPreference.user_id == user_id).first()

    def create_or_update_preference(self, db: Session, user_id: str,
                                    preferred_categories: Optional[List[str]] = None,
                                    min_price: Optional[float] = None,
                                    max_price: Optional[float] = None,
                                    preferred_platforms: Optional[List[str]] = None,
                                    preferred_regions: Optional[List[str]] = None,
                                    min_roi: Optional[float] = None,
                                    min_profit_margin: Optional[float] = None,
                                    keywords: Optional[List[str]] = None,
                                    exclude_keywords: Optional[List[str]] = None,
                                    notification_enabled: Optional[bool] = None) -> UserPreference:
        """创建或更新用户偏好设置"""
        pref = self.get_user_preference(db, user_id)
        
        if pref:
            # 更新现有偏好
            if preferred_categories is not None:
                pref.categories = json.dumps(preferred_categories, ensure_ascii=False)
            if min_price is not None:
                pref.min_price = min_price
            if max_price is not None:
                pref.max_price = max_price
            if preferred_platforms is not None:
                pref.platforms = json.dumps(preferred_platforms, ensure_ascii=False)
            if preferred_regions is not None:
                pref.regions = json.dumps(preferred_regions, ensure_ascii=False)
            if min_roi is not None:
                pref.min_roi = min_roi
            if min_profit_margin is not None:
                pref.min_profit_margin = min_profit_margin
            if keywords is not None:
                pref.keywords = json.dumps(keywords, ensure_ascii=False)
            if exclude_keywords is not None:
                pref.exclude_keywords = json.dumps(exclude_keywords, ensure_ascii=False)
            if notification_enabled is not None:
                pref.notification_enabled = notification_enabled
        else:
            # 创建新偏好
            pref = UserPreference(
                user_id=user_id,
                preferred_categories=json.dumps(preferred_categories or [], ensure_ascii=False),
                min_price=min_price,
                max_price=max_price,
                preferred_platforms=json.dumps(preferred_platforms or [], ensure_ascii=False),
                preferred_regions=json.dumps(preferred_regions or [], ensure_ascii=False),
                min_roi=min_roi,
                min_profit_margin=min_profit_margin,
                keywords=json.dumps(keywords or [], ensure_ascii=False),
                exclude_keywords=json.dumps(exclude_keywords or [], ensure_ascii=False),
                notification_enabled=notification_enabled if notification_enabled is not None else True
            )
            db.add(pref)
        
        db.commit()
        db.refresh(pref)
        return pref

    # ========== Notification Operations ==========
    def create_notification(self, db: Session, user_id: str, notification_type: str,
                            title: str, content: str, data: Optional[Dict[str, Any]] = None,
                            priority: str = "normal") -> Notification:
        """创建通知"""
        notification = Notification(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            content=content,
            data=json.dumps(data or {}, ensure_ascii=False),
            priority=priority
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification

    def get_notifications(self, db: Session, user_id: str, is_read: Optional[bool] = None,
                          skip: int = 0, limit: int = 20) -> List[Notification]:
        """获取用户通知列表"""
        query = db.query(Notification).filter(Notification.user_id == user_id)
        if is_read is not None:
            query = query.filter(Notification.is_read == is_read)
        return query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()

    def mark_notification_read(self, db: Session, notification_id: int) -> bool:
        """标记通知为已读"""
        notification = db.query(Notification).filter(Notification.id == notification_id).first()
        if not notification:
            return False
        notification.is_read = True
        notification.read_at = datetime.now()
        db.commit()
        return True

    def create_trend_alert(self, db: Session, user_id: str, category: str,
                           growth_rate: float, summary: str, hot_keywords: List[str]) -> Notification:
        """创建趋势警报通知"""
        data = {
            "category": category,
            "growth_rate": growth_rate,
            "hot_keywords": hot_keywords
        }
        
        priority = "high" if growth_rate > 50 else "urgent" if growth_rate > 100 else "normal"
        
        title = f"趋势警报：{category} 增长率 {growth_rate}%"
        content = f"{category} 品类出现高增长趋势（增长率 {growth_rate}%）\n\n摘要：{summary}\n\n热门关键词：{', '.join(hot_keywords)}"
        
        return self.create_notification(db, user_id, "trend_alert", title, content, data, priority)

    # ========== Smart Recommendation Operations ==========
    def recommend_products(self, db: Session, user_id: str, limit: int = 10) -> List[Product]:
        """基于用户偏好推荐产品"""
        pref = self.get_user_preference(db, user_id)
        if not pref:
            # 无偏好设置，返回潜力分最高的产品
            return db.query(Product).filter(
                Product.status == 'active',
                Product.potential_score >= 7
            ).order_by(Product.potential_score.desc()).limit(limit).all()
        
        query = db.query(Product).filter(Product.status == 'active')
        
        # 解析偏好
        categories = []
        if pref.preferred_categories is not None:
            try:
                categories = json.loads(pref.preferred_categories)
            except:
                pass
        
        if categories:
            query = query.filter(Product.category.in_(categories))
        
        if pref.min_price:
            query = query.filter(Product.purchase_price >= pref.min_price)
        
        if pref.max_price:
            query = query.filter(Product.purchase_price <= pref.max_price)
        
        if pref.min_roi:
            query = query.filter(Product.roi >= pref.min_roi)
        
        if pref.min_profit_margin:
            query = query.filter(Product.profit_margin >= pref.min_profit_margin)
        
        # 按潜力分数和ROI排序
        return query.order_by(
            Product.potential_score.desc(),
            Product.roi.desc()
        ).limit(limit).all()

    # ========== Batch Import Operations ==========
    def batch_import_suppliers(self, db: Session, suppliers_data: List[Dict[str, Any]],
                                source: str = "batch_import") -> Dict[str, Any]:
        """批量导入供应商数据"""
        success_count = 0
        failed_count = 0
        failed_items = []
        
        for idx, item in enumerate(suppliers_data):
            try:
                supplier_in = SupplierCreate(
                    name=item.get('name', f'供应商_{idx}'),
                    company_name=item.get('company_name'),
                    contact_person=item.get('contact_person'),
                    contact_phone=item.get('contact_phone'),
                    contact_email=item.get('contact_email'),
                    wechat_id=item.get('wechat_id'),
                    region=item.get('region'),
                    address=item.get('address'),
                    platform=item.get('platform'),
                    platform_url=item.get('platform_url'),
                    min_order_quantity=item.get('min_order_quantity'),
                    is_verified=item.get('is_verified', False),
                    rating=item.get('rating'),
                    categories=item.get('categories', []),
                    tags=item.get('tags', []),
                    notes=item.get('notes'),
                    source=source
                )
                self.create_supplier(db, supplier_in)
                success_count += 1
            except Exception as e:
                failed_count += 1
                failed_items.append({
                    "index": idx,
                    "data": item,
                    "error": str(e)
                })
        
        return {
            "total": len(suppliers_data),
            "success": success_count,
            "failed": failed_count,
            "failed_items": failed_items
        }
