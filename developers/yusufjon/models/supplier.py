from sqlalchemy import Column, Date, Integer, Numeric, DateTime, Time, String, Boolean, Text, ForeignKey, func
from databases.main import Base
from sqlalchemy.orm import relationship, backref


class Supplier(Base):
    __tablename__ = "supplier"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, default='')
    balance = Column(Numeric, default=0)
    created_at = Column(Date, default=func.now())
    disabled = Column(Boolean, default=False)
   