from sqlalchemy import Column, Date, Integer, Numeric, DateTime, Time, String, Boolean, Text, ForeignKey, func
from databases.main import Base
from sqlalchemy.orm import relationship, backref
from developers.yusufjon.models.product import *
from developers.yusufjon.models.user import *
from developers.yusufjon.models.plant import *


class Utilization(Base):
    __tablename__ = "utilization"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey('product.id'), default=0)
    type = Column(String(255))
    user_id = Column(Integer, ForeignKey('user.id'), default=0)
    datetime = Column(DateTime, default=func.now())
    value = Column(Numeric)
    plant_id = Column(Integer, ForeignKey('plant.id'), default=0)
    cost = Column(Numeric, default=0)

    item = relationship("Product", backref="utilizations")
    user = relationship("User", backref="utilizations")
    plant = relationship("Plant", backref="utilizations")

