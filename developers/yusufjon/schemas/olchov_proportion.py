from enum import Enum
from pydantic import BaseModel
from developers.yusufjon.models.olchov_proportion import *

class NewOlchov_Proportion(BaseModel):
    abs_olchov_id: int
    rel_olchov_id: int
    value: float


class UpdateOlchov_Proportion(BaseModel):
    abs_olchov_id: int
    rel_olchov_id: int
    value: float

        
