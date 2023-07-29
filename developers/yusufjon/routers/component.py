from fastapi import HTTPException, APIRouter, Depends, status
from typing import Optional
from developers.yusufjon.schemas.user import NewUser
from security.auth import get_current_active_user
from databases.main import ActiveSession
from sqlalchemy.orm import joinedload, Session
from developers.yusufjon.models.component import *
from developers.yusufjon.functions.component import *
from developers.yusufjon.schemas.component import *

component_router = APIRouter(tags=['Component Endpoint'])

@component_router.get("/components", description="This router returns list of the components using pagination")
async def get_components_list(
    search: Optional[str] = "",
    cycle_id: Optional[int] = 0,
    disabled: Optional[bool] = False,
    page: int = 1,
    limit: int = 10,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):   
    if usr.role in ['admin', 'accountant', 'analyst']:
        return get_all_components(search, cycle_id, disabled, page, limit, usr, db)  
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")  

@component_router.post("/component/create", description="This router is able to add new component")
async def create_new_component(
    form_data: NewComponent,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst']:
        return create_component(form_data, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")

@component_router.put("/component/{id}/update", description="This router is able to update component")
async def update_one_component(
    id: int,
    form_data: UpdateComponent,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst']:
        return update_component(id, form_data, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")
    
@component_router.delete("/component/{id}/delete", description="This router is able to delete component")
async def delete(
    id: int,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst']:
        return delete_component(id,db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")
