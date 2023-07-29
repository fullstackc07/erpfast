from developers.yusufjon.utils.main import *
from developers.yusufjon.models.phone import *

class NewPhone(BaseModel):
    number: str
    owner_id: int
    ownertype: str

class PhoneNum(BaseModel):
    number: str


class UpdatePhone(BaseModel):
    number: str
    owner_id: int
    ownertype: str

        
