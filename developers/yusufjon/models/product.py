from sqlalchemy import Column, Date, Integer, Numeric, DateTime, Time, String, Boolean, Text, ForeignKey, func
from databases.main import Base
from sqlalchemy.orm import relationship, backref
from developers.yusufjon.models.product_type import * 
from developers.yusufjon.models.olchov import * 


class Product(Base):
    __tablename__ = "product"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, default='')
    product_type_id = Column(Integer, ForeignKey('product_type.id'), default=0)
    image = Column(Text, default='')
    unit = Column(Boolean, default=False)
    olchov_id = Column(Integer, ForeignKey('olchov.id'), default=0)
    disabled = Column(Boolean, default=False)
    plant_price = Column(Numeric, default=0)
    trade_price = Column(Numeric, default=0)
    alarm_value = Column(Numeric, default=0)

    product_type = relationship('Product_Type', backref='products')
    olchov = relationship('Olchov', backref='products')

