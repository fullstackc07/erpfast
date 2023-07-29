from enum import Enum
from pydantic import BaseModel
from developers.yusufjon.models.product import *

class NewProduct(BaseModel):
    name: str
    product_type_id: int
    image: dict
    unit: bool
    olchov_id: int
    disabled: bool


class UpdateProduct(BaseModel):
    name: str
    product_type_id: int
    image: dict
    unit: bool
    olchov_id: int
    disabled: bool

        
