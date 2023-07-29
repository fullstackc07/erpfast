from enum import Enum
from pydantic import BaseModel
from developers.yusufjon.models.product_type import *
from typing import Optional

class NewProduct_Type(BaseModel):
    name: str
    code: str
    status: str
    image: dict
    olchov_id: int
    detail: Optional[bool] = False


class UpdateProduct_Type(BaseModel):
    name: str
    code: str
    status: str
    image: dict
    olchov_id: int
    detail: bool
        
