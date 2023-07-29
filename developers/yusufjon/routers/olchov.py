from fastapi import HTTPException, APIRouter, Depends
from typing import Optional
from developers.yusufjon.schemas.user import NewUser
from security.auth import get_current_active_user
from databases.main import ActiveSession
from sqlalchemy.orm import joinedload, Session
from developers.yusufjon.models.olchov import *
from developers.yusufjon.functions.olchov import *
from developers.yusufjon.schemas.olchov import *

olchov_router = APIRouter(tags=['Olchov Endpoint'])

@olchov_router.get("/olchovs", description="This router returns list of the olchovs using pagination")
async def get_olchovs_list(
    search: Optional[str] = "",
    page: int = 1,
    limit: int = 10,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):   
    if usr.role in ['admin', 'accountant', 'analyst']:
        return get_all_olchovs(search, page, limit, usr, db)  
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")  

@olchov_router.post("/olchov/create", description="This router is able to add new olchov")
async def create_new_olchov(
    form_data: NewOlchov,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst']:
        return create_olchov(form_data, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")

@olchov_router.put("/olchov/{id}/update", description="This router is able to update olchov")
async def update_one_olchov(
    id: int,
    form_data: UpdateOlchov,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst']:
        return update_olchov(id, form_data, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")
