from enum import Enum
from pydantic import BaseModel

class UserRoles(str, Enum):
    admin ="admin"
    accountant ='accountant'
    analyst ='analyst'
    seller ='seller'
    worker ='worker'
    plant_admin ='plant_admin'
    seller_admin ='seller_admin'
    storeman='storeman'

class NewUser(BaseModel):
    name: str
    nation: str
    birthdate: str
    specialty: str
    passport: int
    workbegindate: str
    salary: float
    username: str
    passwordhash: int
    disabled: bool
    role: int
    agreement_expiration: str


class UpdateUser(BaseModel):
    name: str
    nation: str
    birthdate: str
    specialty: str
    passport: int
    workbegindate: str
    salary: float
    username: str
    passwordhash: int
    disabled: bool
    role: int
    agreement_expiration: str

        
