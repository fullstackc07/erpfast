from sqlalchemy import Column, Date, Integer, Numeric, DateTime, Time, String, Boolean, Text, ForeignKey, func
from databases.main import Base
from sqlalchemy.orm import relationship, backref
from developers.yusufjon.models.product_type import * 
from developers.yusufjon.models.material_type import * 
from developers.yusufjon.models.cycle import * 


class Component(Base):
    __tablename__ = "component"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_type_id = Column(Integer, ForeignKey('product_type.id'), default=0)
    material_type_id = Column(Integer, ForeignKey('material_type.id'), default=0)
    cycle_id = Column(Integer, ForeignKey('cycle.id'), default=0)
    disabled = Column(Boolean, default=False)
    value = Column(Numeric)

    product_type = relationship('Product_Type', backref='components')
    material_type = relationship('Material_Type', backref='components')
    cycle = relationship('Cycle', backref='components')
    

