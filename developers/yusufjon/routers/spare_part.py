from fastapi import HTTPException, APIRouter, Depends
from typing import Optional
from developers.yusufjon.schemas.user import NewUser
from security.auth import get_current_active_user
from databases.main import ActiveSession
from sqlalchemy.orm import joinedload, Session
from developers.yusufjon.models.spare_part import *
from developers.yusufjon.functions.spare_part import *
from developers.yusufjon.schemas.spare_part import *

spare_part_router = APIRouter(tags=['Spare part Endpoint'])


@spare_part_router.get("/spare_part", description="This router returns list of spare parts using pagination")
async def get_spare_parts_list(
    search: Optional[str] = "",
    page: int = 1,
    limit: int = 10,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):   
    if usr.role in ['admin', 'accountant', 'analyst']:
        return get_all_spare_parts(search, page, limit, usr, db)  
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")  


@spare_part_router.post("/spare_part/update_id", description="This router is able to add new spare part")
async def spare_part_update_id(
    id: int,
    value: float,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst']:
        return update_new_sparePart(id, value, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")
    

@spare_part_router.post("/spare_part/create", description="This router is able to add new spare part")
async def create_spare_part(
    form_data: New_spare_part,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst']:
        return create_new_spare_part(form_data, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")



@spare_part_router.put("/spare_part/{id}/update", description="This router is able to update spare part")
async def put_update_spare_part(
    id: int,
    form_data: New_spare_part,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst']:
        return update_spare_part(id, form_data, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")
