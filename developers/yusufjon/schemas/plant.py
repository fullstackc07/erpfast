from enum import Enum
from typing import List, Optional
from pydantic import BaseModel
from developers.yusufjon.models.plant import *
from developers.yusufjon.schemas.plant_user import NewPlantUser

class NewPlant(BaseModel):
    name: str
    kpi: Optional[float] = 0
    plant_users: Optional[List[NewPlantUser]] = []

class UpdatePlant(BaseModel):
    name: str
    disabled: bool
    kpi: Optional[float] = 0

        
