from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from security.auth import get_current_active_user
from databases.main import ActiveSession
from developers.yusufjon.schemas.user import NewUser
from ..functions.loans import *
from datetime import date


loans_router = APIRouter(tags=['Loans'])


@loans_router.get("/get_loans")
def get_loans(from_time: date = None, to_time: date = None, customer_id: int = 0, id: int = 0, status: bool = None, market_id: int = 0, page: int = 1, limit: int = 25, db: Session = ActiveSession, current_user: NewUser = Depends(get_current_active_user)):
    if page <= 0 or limit < 0 :
        raise HTTPException(status_code = 400, detail = "page yoki limit 0 dan kichik kiritilmasligi kerak")
    if current_user.role not in ["admin", "seller", "seller_admin"] :
        raise HTTPException(status_code = 400, detail = "Sizga ruhsat berilmagan")
    if id :
        return one_loan(id, db)
    return all_loans(from_time, to_time, customer_id, status, market_id, page, limit, db)