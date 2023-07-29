from enum import Enum
from pydantic import BaseModel
from developers.yusufjon.models.building import *

class NewBuilding(BaseModel):
    name: str


class UpdateBuilding(BaseModel):
    name: str
    disabled: int

        
