from sqlalchemy import Column, Date, Integer, Numeric, String, Boolean, Text, ForeignKey
from databases.main import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String)
    nation = Column(String)
    birthDate = Column(Date)
    specialty = Column(String, default='')
    passport = Column(Text)
    workBeginDate = Column(Date, nullable=True)
    salary = Column(Numeric, nullable=True)
    kpi = Column(Numeric, nullable=True)
    username = Column(String, nullable=True)
    passwordHash = Column(Integer, nullable=True)
    disabled = Column(Boolean, nullable =True)
    role = Column(Integer, nullable=True)
    agreement_expiration = Column(Date, nullable=True)
    balance = Column(Date, default=0)
    market_id = Column(Integer, default = 0)
    salaryDay = Column(Integer, default = 1)
    address = Column(String, default = "")
    shift_id = Column(Integer, ForeignKey("shift.id"))

    shift = relationship("Shift")