from sqlalchemy import Column, Date, Integer, Numeric, DateTime, Time, String, Boolean, Text, ForeignKey, func
from databases.main import Base
from sqlalchemy.orm import relationship, backref
from developers.yusufjon.models.cycle import * 


class Work(Base):
    __tablename__ = "work"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cycle_id = Column(Integer, ForeignKey('cycle.id'), default=0)
    name = Column(String, default='')
    disabled = Column(Boolean, default=False)

    cycle = relationship('Cycle', backref='works')

