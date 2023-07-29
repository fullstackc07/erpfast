from sqlalchemy import Column, Date, Integer, Numeric, DateTime, Time, String, Boolean, Text, ForeignKey, func
from databases.main import Base
from sqlalchemy.orm import relationship, backref


class Shift(Base):
    __tablename__ = "shift"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), unique=True)
    from_time = Column(Time, default=func.now())
    to_time = Column(Time, default=func.now())


