from fastapi import HTTPException, APIRouter, Depends
from typing import Optional
from developers.yusufjon.schemas.user import NewUser
from security.auth import get_current_active_user
from databases.main import ActiveSession
from sqlalchemy.orm import joinedload, Session
from developers.yusufjon.models.utilization import *
from developers.yusufjon.functions.utilization import *
from developers.yusufjon.schemas.utilization import *

utilization_router = APIRouter(tags=['Utilization Endpoint'])


@utilization_router.get("/utilization", description="This router returns list of utilization using pagination")
async def get_utilization_list(
    type: Optional[str] = "",
    page: int = 1,
    limit: int = 10,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):   
    if usr.role in ['admin', 'accountant', 'analyst']:
        return get_all_utilization(type, page, limit, usr, db)  
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")  


@utilization_router.put("/utilization/{id}/update", description="This router is able to update utilization")
async def update_utilization(
    id: int,
    form_data: Update_utilization,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst']:
        return update_utilization(id, form_data, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")