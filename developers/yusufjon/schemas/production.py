from typing import Optional
from pydantic import BaseModel, Field, validator
from developers.yusufjon.models.production import *
from databases.main import SessionLocal
from datetime import date

class NewProduction(BaseModel):
    product_cycle_id: int
    material_id: int
    plan_id: int
    plant_id: int
    next_plant_id: Optional[int] = 0
    value: float = Field(..., ge=0)
    size1: float = Field(0, ge=0)
    size2: float = Field(0, ge=0)
    norm: Optional[float] = Field(0, ge=0)
    trade_id: int
    trade_item_id: int
    period: date = Field(date.today())



class UpdateProduction(BaseModel):
    cycle_id: int
    plant_id: int
    value: Optional[float] = Field(0, ge=0)
    norm: Optional[float] = Field(0, ge=0)

        
