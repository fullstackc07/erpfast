from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from security.auth import get_current_active_user
from databases.main import ActiveSession
from developers.yusufjon.schemas.user import NewUser
from ..functions.fixed_expenses import *
from ..schemas import Fixed_expense, UpdateFixed_expense


fixed_expenses_router = APIRouter(tags=['Fixed Expenses'])


@fixed_expenses_router.get("/get_fixed_expenses")
def get_fixed_expenses(search: str = None, id: int = 0, market_id: int = 0, page: int = 1, limit: int = 25, db: Session = ActiveSession, current_user: NewUser = Depends(get_current_active_user)):
    if page <= 0 or limit < 0 :
        raise HTTPException(status_code = 400, detail = "page yoki limit 0 dan kichik kiritilmasligi kerak")
    if current_user.role not in ["admin", "seller", "seller_admin"] :
        raise HTTPException(status_code = 400, detail = "Sizga ruhsat berilmagan")
    if id > 0 :
        return one_fixed_expense(id, db)
    return all_fixed_expenses(search, market_id, page, limit, db)
    
    
@fixed_expenses_router.post("/create_fixed_expense_r")
def create_fixed_expense_r(new_fixed_expense: Fixed_expense, db: Session = ActiveSession, current_user: NewUser = Depends(get_current_active_user)):
    if current_user.role not in ["seller", "seller_admin"] :
        raise HTTPException(status_code = 400, detail = "Sizga ruhsat berilmagan")
    if create_fixed_expense(new_fixed_expense, current_user, db) :
        raise HTTPException(status_code = 200, detail = "Amaliyot muvaffaqiyatli amalga oshirildi")
    
    
@fixed_expenses_router.put("/update_fixed_expense_r")
def update_fixed_expense_r(this_fixed_expense: UpdateFixed_expense, db: Session = ActiveSession, current_user: NewUser = Depends(get_current_active_user)):
    if current_user.role not in ["seller", "seller_admin"] :
        raise HTTPException(status_code = 400, detail = "Sizga ruhsat berilmagan")
    if update_fixed_expense(this_fixed_expense, current_user, db) :
        raise HTTPException(status_code = 200, detail = "Amaliyot muvaffaqiyatli amalga oshirildi")