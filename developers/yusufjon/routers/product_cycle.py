from fastapi import HTTPException, APIRouter, Depends, Response
from typing import Optional, List
from developers.yusufjon.schemas.user import NewUser
from security.auth import get_current_active_user
from databases.main import ActiveSession
from sqlalchemy.orm import joinedload, Session
from developers.yusufjon.models.product_cycle import *
from developers.yusufjon.functions.product_cycle import *
from developers.yusufjon.schemas.product_cycle import *

product_cycle_router = APIRouter(tags=['Product_Cycle Endpoint'])


@product_cycle_router.get("/product_cycles", description="This router returns list of the product_cycles using pagination")
async def get_product_cycles_list(
    product_id: Optional[int] = 0,
    cycle_id: Optional[int] = 0,
    page: int = 1,
    limit: int = 10,
    all_cycles: bool = False,
    db: Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if not usr.role in ['any_role']:
        return get_all_product_cycles(all_cycles, product_id, cycle_id, page, limit, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")


@product_cycle_router.post("/product_cycle/create", description="This router is able to add new product_cycle")
async def create_new_product_cycle(
    form_datas: List[NewProduct_Cycle],
    db: Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if not usr.role in ['any_role']:
        for form_data in form_datas:
            create_product_cycle(form_data, usr, db)
        
        db.commit()
        return {'detail': "Ma'lumotlar saqlandi!"}
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")


@product_cycle_router.put("/product_cycle/{id}/update", description="This router is able to update product_cycle")
async def update_one_product_cycle(
    id: int,
    form_data: UpdateProduct_Cycle,
    db: Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if not usr.role in ['any_role']:
        return update_product_cycle(id, form_data, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")


@product_cycle_router.put("/update_cycle_position")
async def update_one_cycle_pos(
    form_data: UpdateCyclePosition,
    db: Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if not usr.role in ['any_role']:
        return update_cycle_posistion(form_data, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")
