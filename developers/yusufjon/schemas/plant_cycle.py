from enum import Enum
from pydantic import BaseModel
from developers.yusufjon.models.plant_cycle import *

class NewPlant_Cycle(BaseModel):
    cycle_id: int
    plant_id: int
    disabled: bool
    hidden: bool


class UpdatePlant_Cycle(BaseModel):
    cycle_id: int
    plant_id: int
    disabled: bool
    hidden: bool

        
