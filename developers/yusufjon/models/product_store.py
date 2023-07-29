from sqlalchemy import Column, Date, Integer, Numeric, DateTime, Time, String, Boolean, Text, ForeignKey, func
from databases.main import Base
from sqlalchemy.orm import relationship, backref
from developers.yusufjon.models.product import * 
from developers.yusufjon.models.plant import * 
from developers.abdusamad.models import * 
from .material import Material


class Product_Store(Base):
    __tablename__ = "product_store"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('product.id'), default=0)
    plant_id = Column(Integer, ForeignKey('plant.id'), default=0)
    material_id = Column(Integer, ForeignKey('material.id'), default=0)
    value = Column(Numeric, default=0)
    price = Column(Numeric, default=0)
    size1 = Column(Numeric, default=0)
    size2 = Column(Numeric, default=0)
    trade_price = Column(Numeric, default=0)
    trade_id = Column(Integer, ForeignKey('trades.id'), default=0)
    trade_item_id = Column(Integer, ForeignKey('trade_items.id'), default=0)
    market_id = Column(Integer, ForeignKey('markets.id'), default=0)

    material = relationship('Material')
    market = relationship('Markets', backref='product_stores')
    product = relationship('Product', backref='product_stores')
    plant = relationship('Plant', backref='product_stores')
    trade = relationship('Trades', backref='product_stores')
    trade_item = relationship('Trade_items', backref='product_stores')

