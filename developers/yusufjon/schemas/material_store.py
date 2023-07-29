from enum import Enum
from pydantic import BaseModel
from developers.yusufjon.models.material_store import *

class NewMaterial_Store(BaseModel):
    material_id: int
    plant_id: int
    value: int
    olchov_id: int


class UpdateMaterial_Store(BaseModel):
    material_id: int
    plant_id: int
    value: int
    olchov_id: int

        
