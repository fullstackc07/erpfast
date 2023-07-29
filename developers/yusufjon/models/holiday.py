from sqlalchemy import Column, Integer, String, ForeignKey
from databases.main import Base
from sqlalchemy.orm import relationship, backref


class Holiday(Base):
    __tablename__ = "holiday"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    week_day = Column(String)

    user = relationship('User', backref=backref('holidays'))

