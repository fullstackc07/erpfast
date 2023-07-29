from sqlalchemy import Column, Date, Integer, Numeric, DateTime, Time, String, Boolean, Text, ForeignKey, func
from databases.main import Base
from sqlalchemy.orm import relationship, backref
from developers.yusufjon.models.product import * 
from developers.yusufjon.models.material import * 


class ProductMaterial(Base):
    __tablename__ = "product_material"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('product.id'), default=0)
    material_id = Column(Integer, ForeignKey('material.id'), default=0)
    disabled = Column(Boolean, default=False)

    product = relationship('Product', backref='product_materials', lazy='joined')
    material = relationship('Material', backref='product_materials', lazy='joined')

