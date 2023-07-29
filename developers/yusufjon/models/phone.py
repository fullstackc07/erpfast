from sqlalchemy import Column, Date, Integer, Numeric, String, Boolean, Text, func, and_, ForeignKey
from databases.main import Base
from sqlalchemy.orm import relationship, backref, polymorphic_union
from developers.yusufjon.models.user import User
from developers.yusufjon.models.supplier import Supplier
from developers.abdusamad.models import Customers, Markets


class Phone(Base):
    __tablename__ = "phone"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    number = Column(String)
    owner_id = Column(Integer, default=0)
    ownerType = Column(String, default='')

    user = relationship('User', foreign_keys=[owner_id],
                        primaryjoin=lambda: and_(
        User.id == Phone.owner_id,
        Phone.ownerType == 'user'
    ), backref=backref("phones", lazy="joined"))

    supplier = relationship('Supplier', foreign_keys=[owner_id],
                            primaryjoin=lambda: and_(
        Supplier.id == Phone.owner_id,
        Phone.ownerType == 'supplier'
    ), backref=backref("phones", lazy="joined"))

    customer = relationship('Customers', foreign_keys=[owner_id], 
                            primaryjoin=lambda: and_(
        Customers.id == Phone.owner_id, 
        Phone.ownerType == 'customer'), backref=backref("phones", lazy="joined"))

    market = relationship('Markets', foreign_keys=[owner_id], 
                            primaryjoin=lambda: and_(
        Markets.id == Phone.owner_id, 
        Phone.ownerType == 'market'), backref=backref("phones", lazy="joined"))

