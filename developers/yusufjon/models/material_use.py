from sqlalchemy import Column, Date, Integer, Numeric, DateTime, Time, String, Boolean, Text, ForeignKey, func
from databases.main import Base
from sqlalchemy.orm import relationship, backref
from developers.yusufjon.models.material import * 
from developers.yusufjon.models.production import * 


class Material_Use(Base):
    __tablename__ = "material_use"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    material_id = Column(Integer, ForeignKey('material.id'), default=0)
    value = Column(Numeric, default=0)
    production_id = Column(Integer, ForeignKey('production.id'), default=0)
    price = Column(Boolean, default=False)

    material = relationship('Material', backref='material_uses')
    production = relationship('Production', backref='material_uses')

