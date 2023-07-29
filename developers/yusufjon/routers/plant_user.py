from fastapi import HTTPException, APIRouter, Depends
from typing import Optional
from developers.yusufjon.schemas.user import NewUser
from security.auth import get_current_active_user
from databases.main import ActiveSession
from sqlalchemy.orm import joinedload, Session
from developers.yusufjon.models.plant_user import *
from developers.yusufjon.functions.plant_user import *
from developers.yusufjon.schemas.plant_user import *

plant_user_router = APIRouter(tags=['Plant_User Endpoint'])

@plant_user_router.get("/plant_users", description="This router returns list of the plant_users using pagination")
async def get_plant_users_list(
    search: Optional[str] = "",
    disabled: Optional[bool] = False,
    plant_id: Optional[int] = 0,
    page: int = 1,
    limit: int = 10,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):   
    if usr.role in ['admin', 'accountant', 'analyst']:
        return get_all_plant_users(plant_id, disabled, search, page, limit, usr, db)  
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")  

@plant_user_router.post("/plant_user/create", description="This router is able to add new plant_user")
async def create_new_plant_user(
    form_data: NewPlant_User,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst']:
        return create_plant_user(form_data, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")

@plant_user_router.put("/plant_user/{id}/update", description="This router is able to update plant_user")
async def update_one_plant_user(
    id: int,
    form_data: UpdatePlant_User,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst']:
        return update_plant_user(id, form_data, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")
