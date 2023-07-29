from enum import Enum
from typing import List
from pydantic import BaseModel, validator
from developers.yusufjon.models.product_material import *


class ResponseData(BaseModel):
    id: int
    product_id: int
    material_id: int


class ResponseGet(BaseModel):
    data: ResponseData
    page_count: int
    data_count: int
    current_page: int
    page_limit: int


class Type(str, Enum):
    PRODUCT = 'PRODUCT'
    MATERIAL = 'MATERIAL'


class SchemaPostMy(BaseModel):
    type: Type
    id: int
    values: List[int]

    @validator('id')
    def validate_id_not_0(cls, v):
        if v == 0:
            raise ValueError('"id" 0 qiymat qabul qilmaydi')
        return v

    @validator('values')
    def validate_detail_not_0(cls, v):
        if not v:
            raise ValueError('"values" bo`sh bo`lishi mumkun emas')
        return v
