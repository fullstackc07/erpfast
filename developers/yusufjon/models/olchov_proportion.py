from sqlalchemy import Column, Date, Integer, Numeric, DateTime, Time, String, Boolean, Text, ForeignKey, func
from databases.main import Base
from sqlalchemy.orm import relationship, backref
from developers.yusufjon.models.olchov import * 


class Olchov_Proportion(Base):
    __tablename__ = "olchov_proportion"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    abs_olchov_id = Column(Integer, ForeignKey('olchov.id'), default=0)
    rel_olchov_id = Column(Integer, ForeignKey('olchov.id'), default=0)
    value = Column(Numeric, default=0)

    abs_olchov = relationship('Olchov', foreign_keys=[abs_olchov_id], backref="relatives")
    rel_olchov = relationship('Olchov', foreign_keys=[rel_olchov_id])

