from sqlalchemy import Column, Date, Integer, Numeric, DateTime, Time, String, Boolean, Text, ForeignKey, func
from databases.main import Base
from sqlalchemy.orm import relationship, backref
from developers.yusufjon.models.product import * 
from developers.yusufjon.models.plant import * 
from developers.yusufjon.models.cycle import * 


class Production_Tree(Base):
    __tablename__ = "production_tree"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, default=0)
    for_product_id = Column(Integer, ForeignKey('product.id'), default=0)
    plant_id = Column(Integer, ForeignKey('plant.id'), default=0)
    cycle_id = Column(Integer, ForeignKey('cycle.id'), default=0)
    value = Column(Numeric, default=0)
    ordinate = Column(Integer)

    product = relationship('Product', backref='trees')
    plant = relationship('Plant')
    cycle = relationship('Cycle')

