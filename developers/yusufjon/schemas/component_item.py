from pydantic import BaseModel, Field
from developers.yusufjon.models.component_item import *

class PartComponent_Item(BaseModel):
    material_id: int
    product_id: int
    value: float = Field(..., ge=0)

class NewComponent_Item(BaseModel):
    material_id: int
    product_id: int
    component_id: int
    main: bool = Field(default=False)
    value: float = Field(..., ge=0)


class UpdateComponent_Item(BaseModel):
    material_id: int
    product_id: int
    component_id: int
    main: bool = Field(default=False)
    value: float = Field(..., ge=0)

        
