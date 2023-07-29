from sqlalchemy import Column, Date, Integer, Numeric, DateTime, Time, String, Boolean, Text, ForeignKey, func
from databases.main import Base
from sqlalchemy.orm import relationship, backref
from developers.yusufjon.models.material import * 
from developers.yusufjon.models.plant import * 
from developers.yusufjon.models.olchov import * 


class Material_Store(Base):
    __tablename__ = "material_store"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    material_id = Column(Integer, ForeignKey('material.id'), default=0)
    plant_id = Column(Integer, ForeignKey('plant.id'), default=0)
    value = Column(Integer, default=0)
    price = Column(Numeric)
    olchov_id = Column(Integer, ForeignKey('olchov.id'), default=0)

    material = relationship('Material', backref='material_stores')
    plant = relationship('Plant', backref='material_stores')
    olchov = relationship('Olchov', backref='material_stores')

