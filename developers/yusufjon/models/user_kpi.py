from sqlalchemy import Column, Date, Integer, Numeric, DateTime, Time, String, Boolean, Text, ForeignKey, func
from databases.main import Base
from sqlalchemy.orm import relationship, backref
from developers.yusufjon.models.user import * 
from developers.yusufjon.models.cycle import * 


class User_Kpi(Base):
    __tablename__ = "user_kpi"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'), default=0)
    cycle_id = Column(Integer, ForeignKey('cycle.id'), default=0)
    value = Column(Numeric, default=0)
    disabled = Column(Boolean, default=False)

    user = relationship('User', backref='user_kpis')
    cycle = relationship('Cycle', backref='user_kpis')

