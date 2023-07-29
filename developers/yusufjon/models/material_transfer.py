from sqlalchemy import Column, Date, Integer, Numeric, DateTime, Time, String, Boolean, Text, ForeignKey, func
from databases.main import Base
from sqlalchemy.orm import relationship
from developers.yusufjon.models.material import * 
from developers.yusufjon.models.supplier import * 
from developers.yusufjon.models.olchov import * 
from developers.yusufjon.models.plant import * 
from developers.yusufjon.models.user import * 


class Material_Transfer(Base):

    __tablename__ = "material_transfer"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    material_id = Column(Integer, ForeignKey('material.id'))
    source_id = Column(Integer, ForeignKey('plant.id'))
    created_at = Column(DateTime, default=func.now())
    value = Column(Numeric)
    price = Column(Numeric)
    olchov_id = Column(Integer, ForeignKey('olchov.id'), default=0)
    disabled = Column(Boolean, default=False)
    plant_id = Column(Integer, ForeignKey('plant.id'), default=0)
    user_id = Column(Integer, ForeignKey('user.id'), default=0)

    material = relationship('Material', backref='transfers')
    olchov = relationship('Olchov')
    plant = relationship('Plant', foreign_keys=[plant_id], backref='coming_transfers')
    source = relationship('Plant', foreign_keys=[source_id], backref='leaving_transfers')
    user = relationship('User', backref='material_transfers')

