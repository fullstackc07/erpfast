from enum import Enum
from pydantic import BaseModel
from developers.yusufjon.models.notification import *

class NewNotification(BaseModel):
    title: str
    body: str
    imgurl: str
    user_id: int


class UpdateNotification(BaseModel):
    title: str
    body: str
    imgurl: str
    user_id: int

        
class MessageSchema(BaseModel):
    title: str
    body: str
    imgurl: str
