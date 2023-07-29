from sqlalchemy import Column, Date, Integer, Numeric, DateTime, Time, String, Boolean, Text, ForeignKey, func
from databases.main import Base
from sqlalchemy.orm import relationship, backref
from developers.yusufjon.models.cycle import * 
from developers.yusufjon.models.plant import * 

class Plant_Cycle(Base):
    __tablename__ = "plant_cycle"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cycle_id = Column(Integer, ForeignKey('cycle.id'), default=0)
    plant_id = Column(Integer, ForeignKey('plant.id'), default=0)
    disabled = Column(Boolean, default=False)
    hidden = Column(Boolean, default=False)

    cycle = relationship('Cycle', backref='plant_cycles')
    plant = relationship('Plant', backref='plant_cycles')

