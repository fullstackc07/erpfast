from enum import Enum
from pydantic import BaseModel
from developers.yusufjon.models.product_cycle import *

class NewProduct_Cycle(BaseModel):
    cycle_id: int
    product_id: int


class UpdateProduct_Cycle(BaseModel):
    cycle_id: int
    product_id: int
    disabled: bool
    

        
