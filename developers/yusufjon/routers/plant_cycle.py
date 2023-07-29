from fastapi import HTTPException, APIRouter, Depends
from typing import Optional
from developers.yusufjon.schemas.user import NewUser
from security.auth import get_current_active_user
from databases.main import ActiveSession
from sqlalchemy.orm import joinedload, Session
from developers.yusufjon.models.plant_cycle import *
from developers.yusufjon.functions.plant_cycle import *
from developers.yusufjon.schemas.plant_cycle import *

plant_cycle_router = APIRouter(tags=['Plant_Cycle Endpoint'])

@plant_cycle_router.get("/plant_cycles", description="This router returns list of the plant_cycles using pagination")
async def get_plant_cycles_list(
    search: Optional[str] = "",
    page: int = 1,
    plant_id: Optional[int] = 0,
    cycle_id: Optional[int] = 0,
    disabled: Optional[bool] = False,
    limit: int = 10,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):   
    if usr.role in ['admin', 'accountant', 'analyst']:
        return get_all_plant_cycles(plant_id, cycle_id, search, disabled, page, limit, usr, db)  
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")  

@plant_cycle_router.post("/plant_cycle/create", description="This router is able to add new plant_cycle")
async def create_new_plant_cycle(
    form_data: NewPlant_Cycle,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst']:
        return create_plant_cycle(form_data, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")

@plant_cycle_router.put("/plant_cycle/{id}/update", description="This router is able to update plant_cycle")
async def update_one_plant_cycle(
    id: int,
    form_data: UpdatePlant_Cycle,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst']:
        return update_plant_cycle(id, form_data, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")
