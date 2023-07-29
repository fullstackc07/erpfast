from enum import Enum
from datetime import date
from typing import Optional
from pydantic import BaseModel
from developers.yusufjon.models.plan import *

class NewPlan(BaseModel):
    product_id: int
    value: float
    comment: str
    size1: float
    size2: float
    material_id: int
    to_date: date
    disabled: Optional[bool] = False
