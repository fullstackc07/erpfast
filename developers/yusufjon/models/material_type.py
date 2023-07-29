from sqlalchemy import Column, Date, Integer, Numeric, DateTime, Time, String, Boolean, Text, ForeignKey, func
from databases.main import Base
from sqlalchemy.orm import relationship


class Material_Type(Base):

    __tablename__ = "material_type"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, unique=True)
    image = Column(Text, default='')
    hidden = Column(Boolean, default=False)
    olchov_id  = Column(Integer, ForeignKey("olchov.id"))

    olchov = relationship("Olchov", lazy='joined')

   
   

