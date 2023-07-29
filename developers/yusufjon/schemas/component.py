from enum import Enum
from pydantic import BaseModel, Field
from developers.yusufjon.models.component import *
from . component_item import PartComponent_Item

class ComTypes(str, Enum):
    product = 'product'
    material = 'material'

class PartComponent(BaseModel):
    type: ComTypes
    name: str

class NewComponent(BaseModel):
    type: ComTypes
    name: str
    value: float = Field(..., ge=0)
    cycle_id: int

class UpdateComponent(BaseModel):
    type: ComTypes
    name: str
    cycle_id: int
    value: float = Field(..., ge=0)