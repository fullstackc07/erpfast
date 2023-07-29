from fastapi import HTTPException, APIRouter, Depends
from typing import Optional
from developers.yusufjon.schemas.user import NewUser
from security.auth import get_current_active_user
from databases.main import ActiveSession
from sqlalchemy.orm import joinedload, Session
from developers.yusufjon.models.plant import *
from developers.yusufjon.functions.plant import *
from developers.yusufjon.schemas.plant import *

plant_router = APIRouter(tags=['Plant Endpoint'])

@plant_router.get("/plants", description="This router returns list of the plants using pagination")
async def get_plants_list(
    search: Optional[str] = "",
    disabled: Optional[bool] = False,
    page: int = 1,
    limit: int = 10,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):   
    return get_all_plants(disabled, search, page, limit, usr, db)  

@plant_router.post("/plant/create", description="This router is able to add new plant")
async def create_new_plant(
    form_data: NewPlant,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst']:
        return create_plant(form_data, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")

@plant_router.put("/plant/{id}/update", description="This router is able to update plant")
async def update_one_plant(
    id: int,
    form_data: UpdatePlant,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst']:
        return update_plant(id, form_data, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")
