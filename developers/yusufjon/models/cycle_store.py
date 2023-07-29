from sqlalchemy import Column, Date, Integer, Numeric, DateTime, Time, String, Boolean, Text, ForeignKey, func
from databases.main import Base
from sqlalchemy.orm import relationship, backref
from developers.yusufjon.models.cycle import * 
from developers.yusufjon.models.plant import * 
from developers.yusufjon.models.olchov import * 
from developers.yusufjon.models.product import * 
from .material import Material
from developers.abdusamad.models import Trades, Trade_items


class Cycle_Store(Base):
    __tablename__ = "cycle_store"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cycle_id = Column(Integer, ForeignKey('cycle.id'), default=0)
    product_id = Column(Integer, ForeignKey('product.id'), default=0)
    material_id = Column(Integer, ForeignKey('material.id'), default=0)
    plant_id = Column(Integer, ForeignKey('plant.id'), default=0)
    ordinate = Column(Integer)
    value = Column(Numeric, default=0)
    size1 = Column(Numeric, default=0)
    size2 = Column(Numeric, default=0)
    olchov_id = Column(Integer, ForeignKey('olchov.id'), default=0)
    trade_id = Column(Integer, ForeignKey('trades.id'), default=0)
    price = Column(Numeric, default=0)
    finished = Column(Boolean, default=False)
    period = Column(Date, default=func.now())
    trade_item_id = Column(Integer, ForeignKey('trade_items.id'), default=0)

    material = relationship('Material')
    product = relationship('Product', backref='cycle_stores')
    trade = relationship('Trades', backref='cycle_stores')
    trade = relationship('Trades', backref='cycle_stores')
    cycle = relationship('Cycle', backref='cycle_stores')
    plant = relationship('Plant', backref='cycle_stores')
    olchov = relationship('Olchov', backref='cycle_stores')
    trade_item = relationship('Trade_items', backref='cycle_stores')
    

