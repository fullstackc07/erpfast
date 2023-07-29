from sqlalchemy import Column, Date, Integer, Numeric, DateTime, Time, String, Boolean, Text, ForeignKey, func
from databases.main import Base
from sqlalchemy.orm import relationship, backref
from developers.yusufjon.models.product import * 
from developers.yusufjon.models.user import * 
from .material import Material
from developers.abdusamad.models import * 


class Product_Transfer(Base):
    __tablename__ = "product_transfer"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('product.id'), default=0)
    user_id = Column(Integer, ForeignKey('user.id'), default=0)
    took_user_id = Column(Integer, ForeignKey('user.id'), default=0)
    market_id = Column(Integer, ForeignKey('markets.id'), default=0)
    datetime = Column(DateTime, default=func.now())
    value = Column(Numeric, default=0)
    cost = Column(Numeric, default=0)
    toMarket = Column(Boolean, default=False)
    size1 = Column(Numeric, default=0)
    size2 = Column(Numeric, default=0)
    material_id = Column(Integer, ForeignKey('material.id'), default=0)

    material = relationship('Material')
    product = relationship('Product', backref='product_transfers')
    user = relationship('User', foreign_keys=[user_id], backref='product_transfers')
    took_user = relationship('User', foreign_keys=[took_user_id], backref='accepted_product_transfers')
    market = relationship('Markets', backref='product_transfers')

