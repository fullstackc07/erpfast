from sqlalchemy import Column, Date, Integer, Numeric, DateTime, Time, String, Boolean, Text, ForeignKey, func
from databases.main import Base
from sqlalchemy.orm import relationship, backref
from developers.yusufjon.models.cycle import * 
from developers.yusufjon.models.product import * 


class Product_Cycle(Base):
    __tablename__ = "product_cycle"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cycle_id = Column(Integer, ForeignKey('cycle.id'), default=0)
    disabled = Column(Boolean, default=False)
    product_id = Column(Integer, ForeignKey('product.id'), default=0)
    ordinate = Column(Integer, default=0)
    datetime = Column(DateTime, default=func.now())

    cycle = relationship('Cycle', backref='product_cycles', lazy='joined')
    product = relationship('Product', backref='product_cycles', lazy='joined')

