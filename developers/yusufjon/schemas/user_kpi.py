from enum import Enum
from pydantic import BaseModel
from developers.yusufjon.models.user_kpi import *

class NewUser_Kpi(BaseModel):
    user_id: int
    cycle_id: int
    value: float


class UpdateUser_Kpi(BaseModel):
    user_id: int
    cycle_id: int
    value: float
    disabled: bool

        
