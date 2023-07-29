from sqlalchemy import Column, Date, Integer, Numeric, DateTime, Time, String, Boolean, Text, ForeignKey, func
from databases.main import Base
from sqlalchemy.orm import relationship, backref


class Building(Base):
    __tablename__ = "building"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, default='')
    disabled = Column(Integer, default=0)


