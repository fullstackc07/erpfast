from datetime import date
from pydantic import BaseModel, Field
from ..models.spare_part import *


class New_spare_part(BaseModel):
    product_id: int = Field(..., ge=1)
    plant_id: int = Field(..., ge=1)
    machine_name: str = Field(..., min_length=3)
    updated_date: date
    to_date: date
    

