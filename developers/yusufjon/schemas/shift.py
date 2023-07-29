from enum import Enum
from pydantic import BaseModel
from developers.yusufjon.models.shift import *

class NewShift(BaseModel):
    name: str
    from_time: str
    to_time: str


class UpdateShift(BaseModel):
    name: str
    from_time: str
    to_time: str

        
