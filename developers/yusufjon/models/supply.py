from sqlalchemy import Column, Date, Integer, Numeric, DateTime, Time, String, Boolean, Text, ForeignKey, func
from databases.main import Base
from sqlalchemy.orm import relationship, backref
from developers.yusufjon.models.material import * 
from developers.yusufjon.models.product import * 
from developers.yusufjon.models.product_material import * 
from developers.yusufjon.models.supplier import * 
from developers.yusufjon.models.olchov import * 
from developers.yusufjon.models.plant import * 
from developers.yusufjon.models.user import * 


class Supply(Base):
    __tablename__ = "supply"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    material_id = Column(Integer, ForeignKey('material.id'), default=0)
    product_material_id = Column(Integer, default=0)
    product_id = Column(Integer, ForeignKey('product.id'), default=0)
    cycle_id = Column(Integer, ForeignKey('cycle.id'), default=0)
    supplier_id = Column(Integer, ForeignKey('supplier.id'), default=0)
    created_at = Column(DateTime, default=func.now())
    value = Column(Numeric, default=0)
    price = Column(Numeric, default=0)
    olchov_id = Column(Integer, ForeignKey('olchov.id'), default=0)
    disabled = Column(Boolean, default=False)
    plant_id = Column(Integer, ForeignKey('plant.id'), default=0)
    user_id = Column(Integer, ForeignKey('user.id'), default=0)

    material = relationship('Material', backref='supplies')
    product = relationship('Product', backref='supplies')
    supplier = relationship('Supplier', backref='supplies')
    olchov = relationship('Olchov')
    cycle = relationship('Cycle')
    plant = relationship('Plant', backref='supplies')
    user = relationship('User', backref='supplies')

