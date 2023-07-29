from datetime import date, datetime
from fastapi import HTTPException, APIRouter, Depends
from typing import Optional
from developers.yusufjon.schemas.user import NewUser
from security.auth import get_current_active_user
from databases.main import ActiveSession
from sqlalchemy.orm import joinedload, Session
from ..functions.indicator import *
from ..functions.indicator_table import *


indicator_router = APIRouter(tags=['Indicator Endpoint'])

@indicator_router.get("/indicators_index")
async def get_material_transfers_plants_list(
    from_date: Optional[date] = datetime.now().strftime("%Y-%m-01"),
    to_date: date = datetime.now().strftime("%Y-%m-%d"),
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):   
    if not usr.role in ['any_role']:
        return get_indicators_index(from_date, to_date, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")

@indicator_router.get("/norm_indicators", description="This router returns list of the material_transfers using pagination")
async def get_material_transfers_plants_list(
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):   
    if not usr.role in ['any_role']:
        return get_norms_indicators(usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")  

@indicator_router.get("/get_orders_table")
async def get_material_transfers_plants_list(
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):   
    if usr.role in ['admin', 'accountant', 'analyst']:
        return get_orders_table_func(usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")

@indicator_router.get("/trade_item_status")
async def get_material_transfers_plants_list(
    trade_item_id: int,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):   
    if usr.role in ['admin', 'accountant', 'analyst']:
        return get_trade_item_status(trade_item_id, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")


@indicator_router.get("/orders_status_table")
async def get_material_transfers_plants_list(
    plant_ids: str,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):   
    if usr.role in ['admin', 'accountant', 'analyst', 'seller_admin']:
       return get_orders_status_table(plant_ids, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")