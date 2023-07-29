from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
from developers.yusufjon.models.material import *

class NewMaterial(BaseModel):
    material_type_id: int
    name: str
    alarm_value: float
    price: float = Field(default=0, ge=0)
    olchov_id: int
    unit: Optional[bool] = True
    has_volume: Optional[bool] = False

class Materials(BaseModel):
    material_id: int

class UpdateMaterial(BaseModel):
    material_type_id: int
    name: str
    alarm_value: float
    price: float = Field(default=0, ge=0)
    olchov_id: int
    unit: Optional[bool] = True
    has_volume: Optional[bool] = False

        
