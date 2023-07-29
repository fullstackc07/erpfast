from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from security.auth import get_current_active_user
from databases.main import ActiveSession
from developers.yusufjon.schemas.user import NewUser
from ..functions.expenses import *
from ..schemas import Expense
from datetime import date


expenses_router = APIRouter(tags=['Expenses'])


@expenses_router.get("/get_expenses")
def get_expenses(from_time: date = None, to_time: date = None, kassa_id: int = 0, type: str = None, source: int = 0, market_id: int = 0, page: int = 1, limit: int = 25, db: Session = ActiveSession, current_user: NewUser = Depends(get_current_active_user)):
    if page <= 0 or limit < 0 :
        raise HTTPException(status_code = 400, detail = "page yoki limit 0 dan kichik kiritilmasligi kerak")
    
    if current_user.role not in ["admin", "seller", "seller_admin", "accountant"] :
        raise HTTPException(status_code = 400, detail = "Sizga ruhsat berilmagan")
    return all_expenses(current_user, from_time, to_time, kassa_id, type, source, market_id, page, limit, db)
    
    
@expenses_router.post("/pay_money_r")
def pay_money_r(new_expense: Expense, db: Session = ActiveSession, current_user: NewUser = Depends(get_current_active_user)):
    if current_user.role not in ["seller", "seller_admin", "admin", "accountant"] :
        raise HTTPException(status_code = 400, detail = "Sizga ruhsat berilmagan")
    if pay_money(new_expense, current_user, db) :
        raise HTTPException(status_code = 200, detail = "Amaliyot muvaffaqiyatli amalga oshirildi")