from sqlalchemy import Column, Date, Integer, Numeric, DateTime, Time, String, Boolean, Text, ForeignKey, func
from databases.main import Base
from sqlalchemy.orm import relationship, backref
from developers.yusufjon.models.material_type import * 
from developers.yusufjon.models.olchov import * 


class Material(Base):
    __tablename__ = "material"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    material_type_id = Column(Integer, ForeignKey('material_type.id'), default=0)
    name = Column(String, default='')
    price = Column(Numeric)
    olchov_id = Column(Integer, ForeignKey('olchov.id'), default=0)
    disabled = Column(Boolean, default=False)
    unit = Column(Boolean, default=True)
    has_volume = Column(Boolean, default=False)
    alarm_value = Column(Numeric, default=0)

    material_type = relationship('Material_Type', backref='materials')
    olchov = relationship('Olchov', backref='materials')

