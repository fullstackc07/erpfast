from sqlalchemy import Column, Date, Integer, Numeric, DateTime, Time, String, Boolean, Text, ForeignKey, func
from databases.main import Base
from sqlalchemy.orm import relationship, backref
from developers.yusufjon.models.olchov import * 


class Product_Type(Base):
    __tablename__ = "product_type"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String)
    disabled = Column(Boolean, default=False)
    image = Column(Text, default='')
    olchov_id = Column(Integer, ForeignKey('olchov.id'), default=0)
    detail = Column(Boolean, default=False)
    hasSize = Column(Boolean, default=False)
    isReady = Column(Boolean, default=False)
    number = Column(Integer)

    olchov = relationship('Olchov', backref='product_types', lazy='joined')

