from enum import Enum
from pydantic import BaseModel
from developers.yusufjon.models.work import *

class NewWork(BaseModel):
    cycle_id: int
    name: str


class UpdateWork(BaseModel):
    cycle_id: int
    name: str
    disabled: bool

        
