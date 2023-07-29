from fastapi import HTTPException, APIRouter, Depends
from typing import Optional
from developers.yusufjon.schemas.user import NewUser
from security.auth import get_current_active_user
from databases.main import ActiveSession
from sqlalchemy.orm import joinedload, Session
from developers.yusufjon.models.olchov_proportion import *
from developers.yusufjon.functions.olchov_proportion import *
from developers.yusufjon.schemas.olchov_proportion import *

olchov_proportion_router = APIRouter(tags=['Olchov_Proportion Endpoint'])

@olchov_proportion_router.get("/olchov_proportions", description="This router returns list of the olchov_proportions using pagination")
async def get_olchov_proportions_list(
    abs_olchov_id: int,
    page: int = 1,
    limit: int = 10,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):   
    if usr.role in ['admin', 'accountant', 'analyst']:
        return get_all_olchov_proportions(abs_olchov_id, page, limit, usr, db)  
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")  

@olchov_proportion_router.post("/olchov_proportion/create", description="This router is able to add new olchov_proportion")
async def create_new_olchov_proportion(
    form_data: NewOlchov_Proportion,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst']:
        return create_olchov_proportion(form_data, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")

@olchov_proportion_router.put("/olchov_proportion/{id}/update", description="This router is able to update olchov_proportion")
async def update_one_olchov_proportion(
    id: int,
    form_data: UpdateOlchov_Proportion,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst']:
        return update_olchov_proportion(id, form_data, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")
