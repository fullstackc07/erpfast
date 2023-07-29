from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from developers.yusufjon.models.cycle import *
from . component import PartComponent

class Direction(str, Enum):
    top = 'top'
    bottom = 'bottom'

class NewCycle(BaseModel):
    name: str = Field(..., min_length=3)
    product_type_id: int
    special: Optional[bool] = False
    hasPeriod: Optional[bool] = False
    kpi: float = Field(0, ge=0)
    plan_value: float = Field(0, ge=0)
    plan_day: int = Field(0, ge=0)
    spending_minut: int = Field(0, ge=0)
    components: List[PartComponent]


class UpdateCycle(BaseModel):
    name: str = Field(..., min_length=3)
    kpi: float = Field(0, ge=0)
    spending_minut: int = Field(0, ge=0)
    plan_value: float = Field(0, ge=0)
    special: Optional[bool] = False
    plan_day: int = Field(0, ge=0)
    disabled: Optional[bool] = False
    hasPeriod: Optional[bool] = False

class UpdateCyclePosition(BaseModel):
    id: int = Field(0, ge=0)
    direction: Direction
