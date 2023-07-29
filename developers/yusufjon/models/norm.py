from sqlalchemy import Column, Date, Integer, Numeric, DateTime, Time, String, Boolean, Text, ForeignKey, func
from databases.main import Base
from sqlalchemy.orm import relationship, backref
from developers.yusufjon.models.olchov import * 


class Norm(Base):
    __tablename__ = "norm"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    products = Column(String, default='')
    value = Column(Numeric, default=0)
    disabled = Column(Boolean, default=False)
    olchov_id = Column(Integer, ForeignKey('olchov.id'), default=0)
    plant_id = Column(Integer, ForeignKey('plant.id'), default=0)

    olchov = relationship('Olchov', backref='norms')
    plant = relationship('Plant', backref='norms')

