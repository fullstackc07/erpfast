from enum import Enum
from datetime import date
from typing import List, Optional
from pydantic import BaseModel
from developers.yusufjon.models.spare_part import *

class New_utilization(BaseModel):
    product_id: int
    type: str = 'product'
    value: float
    plant_id: int
    
class Update_utilization(BaseModel):
    item_id:int
    type:str
    value: float
    plant_id: int
    cost:float