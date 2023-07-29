from enum import Enum
from typing import List
from pydantic import BaseModel
from developers.yusufjon.models.supplier import *
from developers.yusufjon.schemas.material import Materials
from developers.yusufjon.schemas.phone import PhoneNum

class NewSupplier(BaseModel):
    name: str
    balance: int
    phones: List[PhoneNum]
    materials: List[Materials]

class UpdateSupplier(BaseModel):
    name: str
    phones: List[PhoneNum]
    materials: List[Materials]
        
