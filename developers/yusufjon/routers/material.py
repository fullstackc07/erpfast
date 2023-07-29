from fastapi import HTTPException, APIRouter, Depends
from typing import Optional
from developers.yusufjon.models.supplier import Supplier
from developers.yusufjon.schemas.user import NewUser
from security.auth import get_current_active_user
from databases.main import ActiveSession
from sqlalchemy.orm import joinedload, Session
from developers.yusufjon.models.material import *
from developers.yusufjon.functions.material import *
from developers.yusufjon.schemas.material import *

material_router = APIRouter(tags=['Material Endpoint'])


@material_router.get("/materials", description="This router returns list of the materials using pagination")
async def get_materials_list(
    material_type_id: Optional[int] = 0,
    search: Optional[str] = "",
    page: int = 1,
    limit: int = 10,
    db: Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if not usr.role in ['any_role']:
        return get_all_materials(material_type_id, search, page, limit, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")


@material_router.post("/material/create", description="This router is able to add new material")
async def create_new_material(
    form_data: NewMaterial,
    db: Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst']:
        return create_material(form_data, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")


@material_router.put("/material/{id}/update", description="This router is able to update material")
async def update_one_material(
    id: int,
    form_data: UpdateMaterial,
    db: Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst']:
        return update_material(id, form_data, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")
