from sqlalchemy import Column, Date, Integer, Numeric, DateTime, Time, String, Boolean, Text, ForeignKey, func
from databases.main import Base
from sqlalchemy.orm import relationship, backref


class Olchov(Base):
    __tablename__ = "olchov"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, default='')


