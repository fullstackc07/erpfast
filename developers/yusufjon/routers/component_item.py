from fastapi import HTTPException, APIRouter, Depends
from typing import Optional
from developers.yusufjon.schemas.user import NewUser
from security.auth import get_current_active_user
from databases.main import ActiveSession
from sqlalchemy.orm import joinedload, Session
from developers.yusufjon.models.component_item import *
from developers.yusufjon.functions.component_item import *
from developers.yusufjon.schemas.component_item import *

component_item_router = APIRouter(tags=['Component_Item Endpoint'])

@component_item_router.get("/component_items", description="This router returns list of the component_items using pagination")
async def get_component_items_list(
    component_id: int,
    search: Optional[str] = "",
    disabled: Optional[bool] = False,
    page: int = 1,
    limit: int = 10,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):   
    if usr.role in ['admin', 'accountant', 'analyst']:
        return get_all_component_items(component_id, search,disabled ,page, limit, usr, db)  
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")  

@component_item_router.post("/component_item/create", description="This router is able to add new component_item")
async def create_new_component_item(
    form_data: NewComponent_Item,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst']:
        return create_component_item(form_data, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")

@component_item_router.put("/component_item/{id}/update", description="This router is able to update component_item")
async def update_one_component_item(
    id: int,
    form_data: UpdateComponent_Item,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst']:
        return update_component_item(id, form_data, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")

@component_item_router.delete("/component_item/{id}/delete", description="This router is able to delete component_item")
async def delete(
    id: int,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst']:
        return delete_component_item(id,db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")
