from sqlalchemy import Column, Date, Integer, Numeric, DateTime, Time, String, Boolean, Text, ForeignKey, func
from databases.main import Base
from sqlalchemy.orm import relationship, backref
from developers.yusufjon.models.product_type import * 


class Cycle(Base):
    __tablename__ = "cycle"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, default='')
    product_type_id = Column(Integer, ForeignKey('product_type.id'), default=0)
    kpi = Column(Numeric, default=0)
    spending_minut = Column(Integer, default=0)
    plan_value = Column(Numeric, default=0)
    plan_day = Column(Integer, default=0)
    special = Column(Boolean, default=False)
    disabled = Column(Boolean, default=False)
    hasPeriod = Column(Boolean, default=True)

    product_type = relationship('Product_Type', backref=backref('cycles'))

