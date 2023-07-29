from enum import Enum
from pydantic import BaseModel
from developers.yusufjon.models.olchov import *

class NewOlchov(BaseModel):
    name: str


class UpdateOlchov(BaseModel):
    name: str

        
