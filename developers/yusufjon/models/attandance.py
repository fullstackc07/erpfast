from sqlalchemy import Column, Date, Integer, Numeric, DateTime, Time, String, Boolean, Text, ForeignKey, func
from databases.main import Base
from sqlalchemy.orm import relationship, backref
from developers.yusufjon.models.user import * 
from developers.yusufjon.models.plant import * 
from developers.yusufjon.models.building import * 


class Attandance(Base):
    __tablename__ = "attandance"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    type = Column(String, default='')
    user_id = Column(Integer, ForeignKey('user.id'), default=0)
    plant_id = Column(Integer, ForeignKey('plant.id'), default=0)
    building_id = Column(Integer, ForeignKey('building.id'), default=0)
    wage = Column(Numeric, default=0)
    authorizator = Column(String, default='')
    datetime = Column(DateTime, default=func.now())

    user = relationship('User', backref=backref('attandances', order_by='desc(Attandance.id)'))
    last_user = relationship('User', backref=backref('last_attandance', order_by='desc(Attandance.id)', uselist=False))
    plant = relationship('Plant', backref='attandances')
    building = relationship('Building', backref='attandances')

