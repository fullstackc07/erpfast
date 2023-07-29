from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from security.auth import get_current_active_user
from databases.main import ActiveSession
from developers.yusufjon.schemas.user import NewUser
from ..functions.statistics import *
from datetime import date


statistics_router = APIRouter(tags=['Statistics'])


@statistics_router.get("/get_statistics")
def get_statistics(from_time: date = None, to_time: date = None, market_id: int = 0, db: Session = ActiveSession, current_user: NewUser = Depends(get_current_active_user)):
    if current_user.role not in ["admin", "seller", "seller_admin"] :
        raise HTTPException(status_code = 400, detail = "Sizga ruhsat berilmagan")
    return statistics(from_time, to_time, market_id, db)


@statistics_router.get("/get_top_product_statistics")
def get_top_product_statistics(from_time: date = None, to_time: date = None, product_id: int = 0, market_id: int = 0, limit: int = 11, db: Session = ActiveSession, current_user: NewUser = Depends(get_current_active_user)):
    if current_user.role not in ["admin", "seller", "seller_admin"] :
        raise HTTPException(status_code = 400, detail = "Sizga ruhsat berilmagan")
    return top_product_statistics(from_time, to_time, product_id, market_id, limit, db)