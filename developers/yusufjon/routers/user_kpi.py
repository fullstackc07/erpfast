from fastapi import HTTPException, APIRouter, Depends
from typing import Optional
from developers.yusufjon.schemas.user import NewUser
from security.auth import get_current_active_user
from databases.main import ActiveSession
from sqlalchemy.orm import joinedload, Session
from developers.yusufjon.models.user_kpi import *
from developers.yusufjon.functions.user_kpi import *
from developers.yusufjon.schemas.user_kpi import *

user_kpi_router = APIRouter(tags=['User_Kpi Endpoint'])

@user_kpi_router.get("/user_kpis", description="This router returns list of the user_kpis using pagination")
async def get_user_kpis_list(
    user_id: Optional[int] = 0,
    cycle_id: Optional[int] = 0,
    search: Optional[str] = "",
    disabled: Optional[bool] = False,
    page: int = 1,
    limit: int = 10,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):   
    if usr.role in ['admin', 'accountant', 'analyst']:
        return get_all_user_kpis(user_id, cycle_id, disabled, search, page, limit, usr, db)  
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")  

@user_kpi_router.post("/user_kpi/create", description="This router is able to add new user_kpi")
async def create_new_user_kpi(
    form_data: NewUser_Kpi,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst']:
        return create_user_kpi(form_data, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")

@user_kpi_router.put("/user_kpi/{id}/update", description="This router is able to update user_kpi")
async def update_one_user_kpi(
    id: int,
    form_data: UpdateUser_Kpi,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst']:
        return update_user_kpi(id, form_data, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")
