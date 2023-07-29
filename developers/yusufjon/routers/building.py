from fastapi import HTTPException, APIRouter, Depends
from typing import Optional
from developers.yusufjon.schemas.user import NewUser
from security.auth import get_current_active_user
from databases.main import ActiveSession
from sqlalchemy.orm import joinedload, Session
from developers.yusufjon.models.building import *
from developers.yusufjon.functions.building import *
from developers.yusufjon.schemas.building import *

building_router = APIRouter(tags=['Building Endpoint'])

@building_router.get("/buildings", description="This router returns list of the buildings using pagination")
async def get_buildings_list(
    search: Optional[str] = "",
    disabled: Optional[bool] = False,
    page: int = 1,
    limit: int = 10,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):   
    if not usr.role in ['any_role']:
        return get_all_buildings(disabled, search, page, limit, usr, db)  
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")  

@building_router.post("/building/create", description="This router is able to add new building")
async def create_new_building(
    form_data: NewBuilding,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if not usr.role in ['any_role']:
        return create_building(form_data, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")

@building_router.put("/building/{id}/update", description="This router is able to update building")
async def update_one_building(
    id: int,
    form_data: UpdateBuilding,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if not usr.role in ['any_role']:
        return update_building(id, form_data, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")
