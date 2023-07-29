from sqlalchemy import Column, Date, Integer, Numeric, DateTime, Time, String, Boolean, Text, ForeignKey, func
from databases.main import Base
from sqlalchemy.orm import relationship, backref
from developers.yusufjon.models.cycle import *
from developers.yusufjon.models.product import *
from developers.yusufjon.models.material import *
from developers.abdusamad.models import *


class Plan(Base):
    __tablename__ = "plan"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('product.id'), default=0)
    material_id = Column(Integer, ForeignKey('material.id'), default=0)
    order_id = Column(Integer, ForeignKey('orders.id'), default=0)
    trade_id = Column(Integer, default=0)
    trade_item_id = Column(Integer, ForeignKey('trade_items.id'), default=0)
    value = Column(Numeric, default=0)
    rest_value = Column(Numeric)
    comment = Column(String, default='')
    bron_value = Column(Numeric, default=0)
    size1 = Column(Numeric, default=0)
    size2 = Column(Numeric, default=0)
    user_id = Column(Integer, ForeignKey('user.id'), default=0)
    from_date = Column(DateTime, default=func.now())
    to_date = Column(DateTime)
    disabled = Column(Boolean, default=False)
    product_type_id = Column(Integer, ForeignKey('product_type.id'), default=0)

    order = relationship('Orders')
    trade_item = relationship('Trade_items')
    material = relationship('Material', lazy='joined')
    product = relationship('Product', backref='plans')
    product_type = relationship('Product_Type',backref='plans')
    user = relationship('User', backref='plans')