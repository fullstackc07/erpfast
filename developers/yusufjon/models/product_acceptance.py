from sqlalchemy import Column, Date, Integer, Numeric, DateTime, Time, String, Boolean, Text, ForeignKey, func
from databases.main import Base
from sqlalchemy.orm import relationship, backref
from developers.yusufjon.models.cycle_store import * 
from developers.yusufjon.models.user import * 
from developers.yusufjon.models.product import * 
from developers.yusufjon.models.plant import * 


class Product_Acceptance(Base):
    __tablename__ = "product_acceptance"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cycle_store_id = Column(Integer, ForeignKey('cycle_store.id'), default=0)
    user_id = Column(Integer, ForeignKey('user.id'), default=0)
    product_id = Column(Integer, ForeignKey('product.id'), default=0)
    plant_id = Column(Integer, ForeignKey('plant.id'), default=0)
    datetime = Column(DateTime, default=func.now())
    value = Column(Numeric, default=0)
    

    cycle_store = relationship('Cycle_Store', backref='product_acceptances')
    user = relationship('User', backref='product_acceptances')
    product = relationship('Product', backref='product_acceptances')
    plant = relationship('Plant', backref='product_acceptances')

