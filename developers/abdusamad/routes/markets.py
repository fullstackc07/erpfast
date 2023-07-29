from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from security.auth import get_current_active_user
from databases.main import ActiveSession
from developers.yusufjon.schemas.user import NewUser
from ..functions.markets import *
from ..schemas import Market, UpdateMarket


markets_router = APIRouter(tags=['Markets'])


@markets_router.get("/get_markets")
def get_markets(search: str = None, id: int = 0, page: int = 1, limit: int = 25, db: Session = ActiveSession, current_user: NewUser = Depends(get_current_active_user)):
    if page <= 0 or limit < 0 :
        raise HTTPException(status_code = 400, detail = "page yoki limit 0 dan kichik kiritilmasligi kerak")
    if current_user.role not in ["admin", "seller", "seller_admin", "plant_admin", 'analyst'] :
        raise HTTPException(status_code = 400, detail = "Sizga ruhsat berilmagan")
    if id > 0 :
        return one_market(id, db)
    return all_markets(search, page, limit, db)


@markets_router.post("/create_market_r")
def create_market_r(new_market: Market, db: Session = ActiveSession, current_user: NewUser = Depends(get_current_active_user)):
    if current_user.role != "admin" :
        raise HTTPException(status_code = 400, detail = "Sizga ruhsat berilmagan")
    if create_market(new_market, current_user, db) :
        raise HTTPException(status_code = 200, detail = "Amaliyot muvaffaqiyatli amalga oshirildi")


@markets_router.put("/update_market_r")
def update_market_r(this_market: UpdateMarket, db: Session = ActiveSession, current_user: NewUser = Depends(get_current_active_user)):
    if current_user.role != "admin" :
        raise HTTPException(status_code = 400, detail = "Sizga ruhsat berilmagan")
    update_market(this_market, current_user, db)
    raise HTTPException(status_code = 200, detail = "Amaliyot muvaffaqiyatli amalga oshirildi")