from sqlalchemy import Column, Date, Integer, Numeric, DateTime, Time, String, Boolean, Text, ForeignKey, func
from databases.main import Base
from sqlalchemy.orm import relationship, backref
from developers.abdusamad.models import Customers
from developers.yusufjon.models.supplier import *
from developers.yusufjon.models.user import *

class Bot_chat(Base):
    __tablename__ = "bot_chat"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    chat_id = Column(Integer)
    user_id = Column(Integer)
    username = Column(String(255), default='')
    login = Column(Boolean, default=False)
    date = Column(Date, default=func.now())
    employee_id = Column(Integer, ForeignKey('user.id'), default=0)
    supplier_id = Column(Integer, ForeignKey('supplier.id'), default=0)
    customer_id = Column(Integer, ForeignKey('customers.id'), default=0)

    user = relationship("User", backref="bot_chats")
    supplier = relationship("Supplier", backref="bot_chats")
    customer = relationship("Customers", backref="bot_chats")



    