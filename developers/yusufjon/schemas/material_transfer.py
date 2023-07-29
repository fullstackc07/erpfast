from enum import Enum
from pydantic import BaseModel, Field
from developers.yusufjon.models.material_transfer import *

class NewMaterial_Transfer(BaseModel):
    material_id: int = Field(..., ge=1)
    source_id: int = Field(..., ge=0)
    value: float = Field(..., ge=0.001)
    plant_id: int = Field(..., ge=0)


class UpdateMaterial_Transfer(BaseModel):
    value: float = Field(..., ge=0.001)

        
