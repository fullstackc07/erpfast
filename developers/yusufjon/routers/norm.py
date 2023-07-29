from fastapi import HTTPException, APIRouter, Depends
from typing import Optional
from developers.yusufjon.schemas.user import NewUser
from security.auth import get_current_active_user
from databases.main import ActiveSession
from sqlalchemy.orm import joinedload, Session
from developers.yusufjon.models.norm import *
from developers.yusufjon.functions.norm import *
from developers.yusufjon.schemas.norm import *

norm_router = APIRouter(tags=['Norm Endpoint'])

@norm_router.get("/norms", description="This router returns list of the norms using pagination")
async def get_norms_list(
    plant_id: Optional[int] = 0,
    page: int = 1,
    limit: int = 10,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):   
    if not usr.role in ['any_role']:
        return get_all_norms(plant_id, page, limit, usr, db)  
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")  

@norm_router.post("/norm/create", description="This router is able to add new norm")
async def create_new_norm(
    form_data: NewNorm,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst']:
        return create_norm(form_data, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")

@norm_router.put("/norm/{id}/update", description="This router is able to update norm")
async def update_one_norm(
    id: int,
    form_data: UpdateNorm,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst']:
        return update_norm(id, form_data, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")
