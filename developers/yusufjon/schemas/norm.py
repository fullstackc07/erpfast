from enum import Enum
from pydantic import BaseModel
from typing import List
from developers.yusufjon.models.norm import *

class NewNorm(BaseModel):
    products:str
    plant_id: int
    value: float
    olchov_id: int


class UpdateNorm(BaseModel):
    products:str
    plant_id: int
    value: float
    olchov_id: int
    disabled: bool

        
