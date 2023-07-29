from sqlalchemy import Column, Date, Integer, Numeric, DateTime, Time, String, Boolean, Text, ForeignKey, func
from databases.main import Base
from sqlalchemy.orm import relationship, backref
from developers.yusufjon.models.plant import * 
from developers.yusufjon.models.user import User 
from developers.yusufjon.models.shift import * 
from sqlalchemy import and_


class Plant_User(Base):
    __tablename__ = "plant_user"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    plant_id = Column(Integer, ForeignKey('plant.id'), default=0)
    user_id = Column(Integer, default=0)
    admin = Column(Boolean, default=False)
    disabled = Column(Boolean, default=False)

    plant = relationship('Plant', backref='plant_users')

    user = relationship('User', foreign_keys=[user_id],
                        primaryjoin=lambda: and_(
                                 User.id == Plant_User.user_id,
                        ), backref="plant_users")



