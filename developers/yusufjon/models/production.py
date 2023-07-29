from sqlalchemy import Column, Date, Integer, Numeric, DateTime, Time, String, Boolean, Text, ForeignKey, func
from databases.main import Base
from sqlalchemy.orm import relationship, backref
from developers.yusufjon.models.cycle import * 
from developers.yusufjon.models.product import * 
from developers.yusufjon.models.product_type import * 
from developers.yusufjon.models.plant import * 
from developers.yusufjon.models.user import * 
from developers.abdusamad.models import Trades, Trade_items

class Production(Base):
    __tablename__ = "production"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cycle_id = Column(Integer, ForeignKey('cycle.id'), default=0)
    material_id = Column(Integer, ForeignKey('material.id'), default=0)
    product_id = Column(Integer, ForeignKey('product.id'), default=0)
    product_type_id = Column(Integer, ForeignKey('product_type.id'), default=0)
    plant_id = Column(Integer, ForeignKey('plant.id'), default=0)
    trade_id = Column(Integer, ForeignKey('trades.id'), default=0)
    trade_item_id = Column(Integer, ForeignKey('trade_items.id'), default=0)
    value = Column(Numeric, default=0)
    size1 = Column(Numeric, default=0)
    size2 = Column(Numeric, default=0)
    norm = Column(Numeric, default=0)
    cycle_store_id = Column(Integer, ForeignKey('cycle_store.id'), default=0)
    product_store_id = Column(Integer, ForeignKey('product_store.id'), default=0)
    user_id = Column(Integer, ForeignKey('user.id'), default=0)
    created_at = Column(DateTime, default=func.now())
    cost = Column(Numeric, default=0)
    finished = Column(Boolean, default=False)
    



    cycle_store = relationship('Cycle_Store')
    product_store = relationship('Product_Store')
    cycle = relationship('Cycle')
    material = relationship('Material')
    trade_item = relationship('Trade_items', backref='production')
    trade = relationship('Trades')
    product = relationship('Product')
    product_type = relationship('Product_Type')
    plant = relationship('Plant')
    user = relationship('User')

