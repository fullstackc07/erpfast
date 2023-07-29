from fastapi import HTTPException, APIRouter, Depends
from typing import Optional
from developers.yusufjon.schemas.user import NewUser
from security.auth import get_current_active_user
from databases.main import ActiveSession
from sqlalchemy.orm import joinedload, Session
from developers.yusufjon.models.plan import *
from developers.yusufjon.functions.plan import *
from developers.yusufjon.schemas.plan import *

plan_router = APIRouter(tags=['Plan Endpoint'])

@plan_router.get("/plans", description="This router returns list of the plans using pagination")
async def get_plans_list(
    product_id: Optional[int] = 0,
    search: Optional[str] = "",
    disabled: Optional[bool] = False,
    page: int = 1,
    limit: int = 10,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):   
    if usr.role in ['admin', 'accountant', 'analyst']:
        return get_all_plans(product_id, search, disabled, page, limit, usr, db)  
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")  

@plan_router.get("/plans/products", description="This router returns list of the plans by products using pagination")
async def get_plans_products_list(
    product_type_id: int,
    search: Optional[str] = "",
    page: int = 1,
    limit: int = 10,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):   
    if usr.role in ['admin', 'accountant', 'analyst']:
        return get_plan_products(search, page, limit, product_type_id, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")  

@plan_router.post("/plans/create", description="This router is able to add new plan")
async def create_plan(
    form_data: NewPlan,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst']:
        return create_new_plan(form_data, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")


@plan_router.put("/plans/{id}/update", description="This router is able to update plan")
async def update_one_shift(
    id: int,
    form_data: NewPlan,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst']:
        return update_plan(id, form_data, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")
