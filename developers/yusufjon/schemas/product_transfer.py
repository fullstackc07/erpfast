from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional


class NewProduct_Transfer(BaseModel):
    product_id: int = Field(..., ge=1)
    market_id: int = Field(..., ge=1)
    value: float = Field(..., ge=0.01)
    material_id: Optional[float] = Field(0, ge=0)
    size1: Optional[float] = Field(0, ge=0)
    size2: Optional[float] = Field(0, ge=0)
    tomarket: Optional[float] = True


class UpdateProduct_Transfer(BaseModel):
    product_id: int
    user_id: int
    market_id: int
    datetime: str
    value: float
    tomarket: bool
