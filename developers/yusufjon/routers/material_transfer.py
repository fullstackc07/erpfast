from datetime import date, datetime
from fastapi import HTTPException, APIRouter, Depends
from typing import Optional
from developers.yusufjon.schemas.user import NewUser
from security.auth import get_current_active_user
from databases.main import ActiveSession
from sqlalchemy.orm import joinedload, Session
from developers.yusufjon.models.material_transfer import *
from developers.yusufjon.functions.material_transfer import *
from developers.yusufjon.schemas.material_transfer import *

material_transfer_router = APIRouter(tags=['Material_Transfer Endpoint'])

@material_transfer_router.get("/material_transfer_plants", description="This router returns list of the material_transfers using pagination")
async def get_material_transfers_plants_list(
    material_id: int,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):   
    if not usr.role in ['any_role']:
        return get_plants_material_transfer(material_id, usr, db)  
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")  



@material_transfer_router.get("/material_transfers", description="This router returns list of the material_transfers using pagination")
async def get_material_transfers_list(
    from_date: Optional[date] = datetime.now().strftime('%Y-%m-01'),
    to_date: Optional[date] = datetime.now().strftime('%Y-%m-%d'),
    search: Optional[str] = "",
    material_id: Optional[int] = 0,
    plant_id: Optional[int] = 0,
    source_id: Optional[int] = 0,
    page: int = 1,
    limit: int = 10,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):   
    if usr.role in ['admin', 'accountant', 'analyst', 'plant_admin']:
        return get_all_material_transfers(from_date, to_date, search, material_id, plant_id, source_id,page, limit, usr, db)  
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")  

@material_transfer_router.post("/material_transfer/create", description="This router is able to add new material_transfer")
async def create_new_material_transfer(
    form_data: NewMaterial_Transfer,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst', 'plant_admin']:
        return create_material_transfer(form_data, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")

@material_transfer_router.delete("/material_transfer/{id}/delete")
async def delete_tranmsfer_material(
    id: int,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin']:
        return delete_m_transfer(id, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")
