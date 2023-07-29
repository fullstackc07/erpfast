from datetime import date, datetime
from fastapi import HTTPException, APIRouter, Depends
from typing import Optional
from developers.yusufjon.schemas.user import NewUser
from security.auth import get_current_active_user
from databases.main import ActiveSession
from sqlalchemy.orm import joinedload, Session
from developers.yusufjon.models.supply import *
from developers.yusufjon.functions.supply import *
from developers.yusufjon.schemas.supply import *


supply_router = APIRouter(tags=['Supply Endpoint'])

@supply_router.get("/supplies", description="This router returns list of the supplies using pagination")
async def get_supplies_list(
    supplier_id: Optional[int] = 0,
    plant_id: Optional[int] = 0,
    material_id: Optional[int] = 0,
    product_id: Optional[int] = 0,
    from_date: Optional[date] = datetime.now().strftime('%Y-%m-01'),
    to_date: Optional[date] = datetime.now().strftime('%Y-%m-%d'),
    search: Optional[str] = "",
    page: int = 1,
    limit: int = 10,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):   
    if usr.role in ['admin', 'accountant', 'analyst', 'plant_admin']:
        return get_all_supplies(supplier_id, plant_id, material_id,product_id,from_date, to_date, search, page, limit, usr, db)  
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")  

@supply_router.post("/supply/create", description="This router is able to add new supply")
async def create_new_supply(
    form_data: NewSupply,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst', 'plant_admin']:
        return create_supply(form_data, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")

@supply_router.put("/supply/{id}/update", description="This router is able to update supply")
async def update_one_supply(
    id: int,
    form_data: UpdateSupply,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst', 'plant_admin']:
        return update_supply(id, form_data, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")
