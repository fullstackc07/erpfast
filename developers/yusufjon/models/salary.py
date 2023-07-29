from sqlalchemy import Column, Date, Integer, Numeric, DateTime, Time, String, Boolean, Text, ForeignKey, func
from databases.main import Base
from sqlalchemy.orm import relationship, backref


class Salary(Base):
    __tablename__ = "salary"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    year = Column(Integer)
    month = Column(Integer)
    salary = Column(Integer)
    daily = Column(Integer, default=0)
    tax = Column(Integer, default=0)
    calculated_wage = Column(Integer, default=0)
    workdays = Column(Integer, default=1)
    additional_wage = Column(Integer, default=0)

    user = relationship("User", backref="salaries")