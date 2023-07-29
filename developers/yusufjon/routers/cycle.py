from fastapi import HTTPException, APIRouter, Depends
from typing import Optional
from developers.yusufjon.schemas.user import NewUser
from security.auth import get_current_active_user
from databases.main import ActiveSession
from sqlalchemy.orm import joinedload, Session
from developers.yusufjon.models.cycle import *
from developers.yusufjon.functions.cycle import *
from developers.yusufjon.schemas.cycle import *

cycle_router = APIRouter(tags=['Cycle Endpoint'])

@cycle_router.get("/cycles", description="This router returns list of the cycles using pagination")
async def get_cycles_list(
    product_type_id: Optional[int] = 0,
    search: Optional[str] = "",
    page: int = 1,
    limit: int = 10,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):   
    if usr.role in ['admin', 'accountant', 'analyst']:
        return get_all_cycles(product_type_id, search, page, limit, usr, db)  
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")  

@cycle_router.post("/cycle/create", description="This router is able to add new cycle")
async def create_new_cycle(
    form_data: NewCycle,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst']:
        return create_cycle(form_data, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")

@cycle_router.put("/cycle/{id}/update", description="This router is able to update cycle")
async def update_one_cycle(
    id: int,
    form_data: UpdateCycle,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst']:
        return update_cycle(id, form_data, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")
    
@cycle_router.put("/update_cycle_position")
async def update_one_cycle_pos(
    form_data: UpdateCyclePosition,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst']:
        return update_cycle_posistion(form_data, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")

# @cycle_router.get("/fix_cycle_ordinates")
# async def update_one_cycle_pos(
#     db:Session = ActiveSession,
# ):
#     products = db.query(Product).filter_by(disabled=False).all()
#     for pr in products:
#         cycles = db.query(Cycle).filter_by(disabled=False, product_id=pr.id).order_by(Cycle.id.asc()).all()
#         ordinate = 1
#         for cy in cycles:
#             db.query(Cycle).filter_by(id=cy.id).update({
#                 Cycle.ordinate:ordinate
#             })
#             ordinate += 1
#     db.commit()
#     return 'success'


