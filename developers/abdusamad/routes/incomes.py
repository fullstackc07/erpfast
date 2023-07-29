from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from security.auth import get_current_active_user
from databases.main import ActiveSession
from developers.yusufjon.schemas.user import NewUser
from ..functions.incomes import *
from datetime import date
from ..schemas import Income_for_loan


incomes_router = APIRouter(tags=['Incomes'])


@incomes_router.get("/get_incomes")
def get_incomes(from_time: date = None, to_time: date = None, order_id: int = 0, loan_id: int = 0, kassa_id: int = 0, user_id: int = 0, type: str = None, market_id: int = 0, page: int = 1, limit: int = 25, db: Session = ActiveSession, current_user: NewUser = Depends(get_current_active_user)):
    if page <= 0 or limit < 0 :
        raise HTTPException(status_code = 400, detail = "page yoki limit 0 dan kichik kiritilmasligi kerak")
    if current_user.role not in ["admin", "seller", "seller_admin"] :
        raise HTTPException(status_code = 400, detail = "Sizga ruhsat berilmagan")
    return all_incomes(from_time, to_time, order_id, loan_id, kassa_id, user_id, type, market_id, page, limit, db)


@incomes_router.post("/take_money_from_loan_r")
def take_money_from_loan_r(income: Income_for_loan, db: Session = ActiveSession, current_user: NewUser = Depends(get_current_active_user)):
    if current_user.role not in ["seller", "seller_admin"] :
        raise HTTPException(status_code = 400, detail = "Sizga ruhsat berilmagan")
    if take_money_from_loan(income, current_user, db) :
        raise HTTPException(status_code = 200, detail = "Amaliyot muvaffaqiyatli amalga oshirildi")


@incomes_router.post("/take_money_from_order_r")
def take_money_from_order_r(income: Income_for_loan, db: Session = ActiveSession, current_user: NewUser = Depends(get_current_active_user)):
    if current_user.role not in ["seller", "seller_admin"] :
        raise HTTPException(status_code = 400, detail = "Sizga ruhsat berilmagan")
    if take_money_from_order(income, current_user, db) :
        raise HTTPException(status_code = 200, detail = "Amaliyot muvaffaqiyatli amalga oshirildi")