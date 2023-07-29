from sqlalchemy import Column, Date, Integer, Numeric, DateTime, Time, String, Boolean, Text, ForeignKey, func
from databases.main import Base
from sqlalchemy.orm import relationship, backref
from developers.yusufjon.models.material import * 
from developers.yusufjon.models.product import * 
from developers.yusufjon.models.component import * 


class Component_Item(Base):
    __tablename__ = "component_item"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    material_id = Column(Integer, ForeignKey('material.id'), default=0)
    product_id = Column(Integer, ForeignKey('product.id'), default=0)
    component_id = Column(Integer, ForeignKey('component.id'), default=0)
    value = Column(Numeric, default=0)
    disabled = Column(Boolean, default=False)
    main = Column(Boolean, default=False)
    
    material = relationship('Material', backref='component_items')
    product = relationship('Product', backref='component_items')
    component = relationship('Component', backref='component_items')

