from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
from developers.yusufjon.models.supply import *


class NewSupply(BaseModel):
    material_id: Optional[int] = Field(0, ge=0)
    product_id: Optional[int] = Field(0, ge=0)
    product_cycle_id: Optional[int] = Field(0, ge=0)
    product_material_id: Optional[int] = Field(0, ge=0)
    supplier_id: int
    value: float = Field(..., ge=0)
    price: float = Field(..., ge=0)
    olchov_id: int = Field(..., ge=0)
    plant_id: Optional[int] = Field(0, ge=0)


class UpdateSupply(BaseModel):
    material_id: Optional[int] = Field(0, ge=0)
    product_id: Optional[int] = Field(0, ge=0)
    supplier_id: int
    value: float = Field(..., ge=0)
    price: float = Field(..., ge=0)
    olchov_id: int
    plant_id: Optional[int] = 0
