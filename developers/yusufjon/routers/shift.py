from fastapi import HTTPException, APIRouter, Depends
from typing import Optional
from developers.yusufjon.schemas.user import NewUser
from security.auth import get_current_active_user
from databases.main import ActiveSession
from sqlalchemy.orm import joinedload, Session
from developers.yusufjon.models.shift import *
from developers.yusufjon.functions.shift import *
from developers.yusufjon.schemas.shift import *

shift_router = APIRouter(tags=['Shift Endpoint'])

@shift_router.get("/shifts", description="This router returns list of the shifts using pagination")
async def get_shifts_list(
    page: int = 1,
    limit: int = 10,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):   
    if usr.role in ['admin', 'accountant', 'analyst']:
        return get_all_shifts(page, limit, usr, db)  
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")  

@shift_router.post("/shift/create", description="This router is able to add new shift")
async def create_new_shift(
    form_data: NewShift,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst']:
        return create_shift(form_data, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")

@shift_router.put("/shift/{id}/update", description="This router is able to update shift")
async def update_one_shift(
    id: int,
    form_data: UpdateShift,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst']:
        return update_shift(id, form_data, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")
