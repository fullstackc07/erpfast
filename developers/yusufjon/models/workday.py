from sqlalchemy import Column, Date, Integer, Numeric, String, ForeignKey
from databases.main import Base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import and_, func
from ..models.attandance import Attandance
from ..models.user import User


class Workday(Base):
    __tablename__ = "workday"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    salary_id = Column(Integer, ForeignKey("salary.id"))
    date = Column(Date)
    value = Column(Numeric)
    type = Column(String, default='stavka')

    user = relationship("User")
    salary = relationship("Salary", backref=backref("allworkdays", order_by="Workday.date.asc()"))
    attandances = relationship("Attandance", foreign_keys=[user_id], primaryjoin=lambda: and_(Workday.user_id == Attandance.user_id, Workday.date==func.date(Attandance.datetime)), uselist=True, order_by="Attandance.datetime.asc()")