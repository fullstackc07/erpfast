from sqlalchemy import Column, Date, Integer, Numeric, DateTime, Time, String, Boolean, Text, ForeignKey, func
from databases.main import Base
from sqlalchemy.orm import relationship, backref
from ..models.product import *
from ..models.plant import *

class Spare_part(Base):
    __tablename__ = "spare_part"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    machine_name = Column(String(255))
    updated_date = Column(DateTime, default=func.now())
    to_date = Column(DateTime)
    muddat = Column(Integer)
    reminded = Column(Boolean, default=False)
    product_id = Column(Integer, ForeignKey('product.id'), default=0)
    plant_id = Column(Integer, ForeignKey('plant.id'), default=0)

    product = relationship("Product", backref="spare_parts")
    plant = relationship("Plant", backref="spare_parts")


