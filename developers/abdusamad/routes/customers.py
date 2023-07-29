from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from security.auth import get_current_active_user
from databases.main import ActiveSession
from developers.yusufjon.schemas.user import NewUser
from ..functions.customers import *
from ..schemas import Customer, UpdateCustomer


customers_router = APIRouter(tags=['Customers'])


@customers_router.get("/get_customers")
def get_customers(search: str = None, id: int = 0, market_id: int = 0, page: int = 1, limit: int = 25, db: Session = ActiveSession, current_user: NewUser = Depends(get_current_active_user)):
    if page <= 0 or limit < 0 :
        raise HTTPException(status_code = 400, detail = "page yoki limit 0 dan kichik kiritilmasligi kerak")
    if current_user.role not in ["admin", "seller", "seller_admin"] :
        raise HTTPException(status_code = 400, detail = "Sizga ruhsat berilmagan")
    if id > 0 :
        return one_customer(id, db)
    return all_customers(search, market_id, page, limit, db)


@customers_router.post("/create_customer_r")
async def create_customer_r(new_customer: Customer, db: Session = ActiveSession, current_user: NewUser = Depends(get_current_active_user)):
    if current_user.role not in ["seller", "seller_admin"] :
        raise HTTPException(status_code = 400, detail = "Sizga ruhsat berilmagan")
    return create_customer(new_customer, current_user, db)
    # return 1

@customers_router.put("/update_customer_r")
def update_customer_r(this_customer: UpdateCustomer, db: Session = ActiveSession, current_user: NewUser = Depends(get_current_active_user)):
    if current_user.role not in ["seller", "seller_admin"] :
        raise HTTPException(status_code = 400, detail = "Sizga ruhsat berilmagan")
    update_customer(this_customer, current_user, db)
    raise HTTPException(status_code = 200, detail = "Amaliyot muvaffaqiyatli amalga oshirildi")