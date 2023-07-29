from enum import Enum
from pydantic import BaseModel
from developers.yusufjon.models.material_type import *

class NewMaterial_Type(BaseModel):
    name: str
    image: dict
    hidden: bool
    olchov_id: int


class UpdateMaterial_Type(BaseModel):
    name: str
    image: dict
    hidden: bool
    olchov_id: int

        
