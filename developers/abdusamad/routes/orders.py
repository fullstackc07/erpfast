from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from security.auth import get_current_active_user
from databases.main import ActiveSession
from developers.yusufjon.schemas.user import NewUser
from ..functions.orders import *
from datetime import date
from ..schemas import OrderConfirmation, Order, Attach_customer_to_order, Update_delivery_date_for_pre_order


orders_router = APIRouter(tags=['Orders'])


@orders_router.get("/get_orders")
def get_orders(from_time: date = None, to_time: date = None, customer_id: int = 0, user_id: int = 0, status: str = None, id: int = 0, market_id: int = 0, page: int = 1, limit: int = 25, db: Session = ActiveSession, current_user: NewUser = Depends(get_current_active_user)):
    if page <= 0 or limit < 0 :
        raise HTTPException(status_code = 400, detail = "page yoki limit 0 dan kichik kiritilmasligi kerak")
    if current_user.role not in ["admin", "seller", "seller_admin"] :
        raise HTTPException(status_code = 400, detail = "Sizga ruhsat berilmagan")
    if id > 0 :
        return one_order2(id, db)
    return all_orders(from_time, to_time, customer_id, user_id, status, market_id, page, limit, db)
    
    
@orders_router.post("/create_order_r")
def create_customer_r(form: Order, db: Session = ActiveSession, current_user: NewUser = Depends(get_current_active_user)):
    if current_user.role not in ["seller", "seller_admin"] :
        raise HTTPException(status_code = 400, detail = "Sizga ruhsat berilmagan")
    if create_order(form, current_user, db) :
        raise HTTPException(status_code = 200, detail = "Amaliyot muvaffaqiyatli amalga oshirildi")
    
    
@orders_router.delete("/delete_order_r/{id}")
def delete_order_r(id: int, db: Session = ActiveSession, current_user: NewUser = Depends(get_current_active_user)):
    if current_user.role not in ["seller", "seller_admin"] :
        raise HTTPException(status_code = 400, detail = "Sizga ruhsat berilmagan")
    if delete_order(id, db, current_user) :
        raise HTTPException(status_code = 200, detail = "Amaliyot muvaffaqiyatli amalga oshirildi")
    
    
@orders_router.put("/order_confirmation_r")
def order_confirmation_r(form: OrderConfirmation, db: Session = ActiveSession, current_user: NewUser = Depends(get_current_active_user)):
    if current_user.role not in ["seller", "seller_admin"] :
        raise HTTPException(status_code = 400, detail = "Sizga ruhsat berilmagan")
    if order_confirmation(form, current_user, db) :
        raise HTTPException(status_code = 200, detail = "Amaliyot muvaffaqiyatli amalga oshirildi")
    
    
@orders_router.put("/attach_customer_to_order_r")
def attach_customer_to_order_r(form: Attach_customer_to_order, db: Session = ActiveSession, current_user: NewUser = Depends(get_current_active_user)):
    if current_user.role not in ["seller", "seller_admin"] :
        raise HTTPException(status_code = 400, detail = "Sizga ruhsat berilmagan")
    if attach_customer_to_order(form, current_user, db) :
        raise HTTPException(status_code = 200, detail = "Amaliyot muvaffaqiyatli amalga oshirildi")
    
    
@orders_router.put("/update_delivery_date_for_pre_order_r")
def update_delivery_date_for_pre_order_r(form: Update_delivery_date_for_pre_order, db: Session = ActiveSession, current_user: NewUser = Depends(get_current_active_user)):
    if current_user.role not in ["seller", "seller_admin"] :
        raise HTTPException(status_code = 400, detail = "Sizga ruhsat berilmagan")
    if update_delivery_date_for_pre_order(form, current_user, db) :
        raise HTTPException(status_code = 200, detail = "Amaliyot muvaffaqiyatli amalga oshirildi")