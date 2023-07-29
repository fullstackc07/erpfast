from enum import Enum
from pydantic import BaseModel, Field
from developers.yusufjon.models.plant_user import *
from typing import Optional

# class WagePeriods(str, Enum):
#     hourly="hourly"
#     daily="daily"
#     weekly="weekly"
#     monthly="monthly"

class NewPlantUser(BaseModel):
    user_id: int
    # shift_id: int
    # wage: Optional[float] = Field(0, ge=0)
    # wage_period: Optional[WagePeriods] = 'hourly'
    admin: bool = False

class NewPlant_User(BaseModel):
    plant_id: int
    user_id: int
    # shift_id: int
    admin: bool
    disabled: bool
    # wage: Optional[float] = Field(0, ge=0)
    # wage_period: Optional[WagePeriods] = 'hourly'


class UpdatePlant_User(BaseModel):
    plant_id: int
    user_id: int
    # shift_id: int
    admin: bool
    disabled: bool
    # wage: float = Field(..., ge=0)
    # wage_period: WagePeriods

        
