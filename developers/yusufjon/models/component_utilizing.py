from sqlalchemy import Column, Date, Integer, Numeric, String, func, ForeignKey
from sqlalchemy.orm import relationship
from databases.main import Base


class ComponentUtilizing(Base):
    __tablename__ = "component_utilizing"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    value=Column(Numeric)
    created_at = Column(Date, default=func.now())
    production_id=Column(Integer, ForeignKey("production.id"))
    product_store_id=Column(Integer, default=0)
    cycle_store_id=Column(Integer, default=0)
    material_store_id=Column(Integer, default=0)


    production = relationship("Production", backref='utilizings')