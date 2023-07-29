from sqlalchemy import Column, Date, Integer, Numeric, DateTime, Time, String, Boolean, Text, ForeignKey, func
from databases.main import Base
from sqlalchemy.orm import relationship, backref


class Plant(Base):
    __tablename__ = "plant"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, default='')
    disabled = Column(Boolean, default=False)
    hidden = Column(Boolean, default=False)
    kpi = Column(Numeric, default=0)


