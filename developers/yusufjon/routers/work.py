from fastapi import HTTPException, APIRouter, Depends
from typing import List
from developers.yusufjon.schemas.user import NewUser
from security.auth import get_current_active_user
from databases.main import ActiveSession
from sqlalchemy.orm import joinedload, Session
from developers.yusufjon.models.work import *
from developers.yusufjon.functions.work import *
from developers.yusufjon.schemas.work import *

work_router = APIRouter(tags=['Work Endpoint'])

@work_router.get("/works", description="This router returns list of the works using pagination")
async def get_works_list(
    cycle_id: int,
    page: int = 1,
    limit: int = 10,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):   
    if usr.role in ['admin', 'accountant', 'analyst']:
        return get_all_works(cycle_id, page, limit, usr, db)  
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")  

@work_router.post("/work/create", description="This router is able to add new work")
async def create_new_work(
    form_datas: List[NewWork],
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst']:
        return create_work(form_datas, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")

@work_router.put("/work/{id}/update", description="This router is able to update work")
async def update_one_work(
    id: int,
    form_data: UpdateWork,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst']:
        return update_work(id, form_data, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")
