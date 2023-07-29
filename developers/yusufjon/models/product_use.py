from sqlalchemy import Column, Date, Integer, Numeric, DateTime, Time, String, Boolean, Text, ForeignKey, func
from databases.main import Base
from sqlalchemy.orm import relationship, backref
from developers.yusufjon.models.product import * 
from developers.yusufjon.models.production import * 


class Product_Use(Base):
    __tablename__ = "product_use"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('product.id'), default=0)
    value = Column(Numeric, default=0)
    production_id = Column(Integer, ForeignKey('production.id'), default=0)
    price = Column(Numeric, default=0)

    product = relationship('Product', backref='product_uses')
    production = relationship('Production', backref='product_uses')

