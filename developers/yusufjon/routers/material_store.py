from fastapi import HTTPException, APIRouter, Depends
from typing import Optional
from developers.yusufjon.schemas.user import NewUser
from security.auth import get_current_active_user
from databases.main import ActiveSession
from sqlalchemy.orm import joinedload, Session
from developers.yusufjon.models.material_store import *
from developers.yusufjon.functions.material_store import *
from developers.yusufjon.schemas.material_store import *

material_store_router = APIRouter(tags=['Material_Store Endpoint'])

@material_store_router.get("/material_stores", description="This router returns list of the material_stores using pagination")
async def get_material_stores_list(
    search: Optional[str] = "",
    material_type_id: Optional[int] = 0,
    plant_id: Optional[int] = 0,
    page: int = 1,
    limit: int = 10,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):   
    if not usr.role in ['any_role']:
        return get_all_material_stores(search, material_type_id, plant_id, page, limit, usr, db)  
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")  

# @material_store_router.post("/material_store/create", description="This router is able to add new material_store")
# async def create_new_material_store(
#     form_data: NewMaterial_Store,
#     db:Session = ActiveSession,
#     usr: NewUser = Depends(get_current_active_user)
# ):
#     if not usr.role in ['any_role']:
#         return create_material_store(form_data, usr, db)
#     else:
#         raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")

# @material_store_router.put("/material_store/{id}/update", description="This router is able to update material_store")
# async def update_one_material_store(
#     id: int,
#     form_data: UpdateMaterial_Store,
#     db:Session = ActiveSession,
#     usr: NewUser = Depends(get_current_active_user)
# ):
#     if not usr.role in ['any_role']:
#         return update_material_store(id, form_data, usr, db)
#     else:
#         raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")
