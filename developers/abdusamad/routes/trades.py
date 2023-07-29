from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from security.auth import get_current_active_user
from databases.main import ActiveSession
from developers.yusufjon.schemas.user import NewUser
from ..functions.trades import *
from ..schemas import Trade, Trade_pr_to_pre_order, Trade_comp_item_to_pre_order, Return_product


trades_router = APIRouter(tags=['Trades'])


@trades_router.get("/get_trades")
def get_trades(order_id: int = 0, related_number: bool = True, id: int = 0, page: int = 1, limit: int = 25, db: Session = ActiveSession, current_user: NewUser = Depends(get_current_active_user)):
    if page <= 0 or limit < 0 :
        raise HTTPException(status_code = 400, detail = "page yoki limit 0 dan kichik kiritilmasligi kerak")
    if current_user.role not in ["admin", "seller", "seller_admin"] :
        raise HTTPException(status_code = 400, detail = "Sizga ruhsat berilmagan")
    if id > 0 :
        return one_trade(id, order_id, db)
    return all_trades(order_id, related_number, page, limit, db)


@trades_router.get("/get_trade_items")
def get_trade_items(trade_id: int = 0, db: Session = ActiveSession, current_user: NewUser = Depends(get_current_active_user)):
    if current_user.role not in ["admin", "seller", "seller_admin"] :
        raise HTTPException(status_code = 400, detail = "Sizga ruhsat berilmagan")
    return all_trade_items(trade_id, db)


@trades_router.get("/get_trade_status")
def get_trade_status(order_id: int = 0, db: Session = ActiveSession, current_user: NewUser = Depends(get_current_active_user)):
    if current_user.role not in ["admin", "seller", "seller_admin"] :
        raise HTTPException(status_code = 400, detail = "Sizga ruhsat berilmagan")
    return trade_status(order_id, db)


@trades_router.get("/get_returned_products")
def get_returned_products(order_id: int = 0, market_id: int = 0, page: int = 1, limit: int = 25, db: Session = ActiveSession, current_user: NewUser = Depends(get_current_active_user)):
    if current_user.role not in ["admin", "seller", "seller_admin"] :
        raise HTTPException(status_code = 400, detail = "Sizga ruhsat berilmagan")
    return returned_products(order_id, market_id, page, limit, db)
    
    
@trades_router.post("/sell_product_r")
def sell_product_r(new_trade: Trade, db: Session = ActiveSession, current_user: NewUser = Depends(get_current_active_user)):
    if current_user.role not in ["seller", "seller_admin"] :
        raise HTTPException(status_code = 400, detail = "Sizga ruhsat berilmagan")
    if sell_product(new_trade, current_user, db) :
        raise HTTPException(status_code = 200, detail = "Amaliyot muvaffaqiyatli amalga oshirildi")
    
    
@trades_router.delete("/delete_trade_r/{id}")
def delete_trade_r(id: int, db: Session = ActiveSession, current_user: NewUser = Depends(get_current_active_user)):
    if current_user.role not in ["seller", "seller_admin"] :
        raise HTTPException(status_code = 400, detail = "Sizga ruhsat berilmagan")
    if delete_trade(id, db, current_user) :
        raise HTTPException(status_code = 200, detail = "Amaliyot muvaffaqiyatli amalga oshirildi")
    
    
@trades_router.post("/return_product_r")
def return_product_r(form: Return_product, db: Session = ActiveSession, current_user: NewUser = Depends(get_current_active_user)):
    if current_user.role not in ["seller", "seller_admin"] :
        raise HTTPException(status_code = 400, detail = "Sizga ruhsat berilmagan")
    if return_product(form, db, current_user) :
        raise HTTPException(status_code = 200, detail = "Amaliyot muvaffaqiyatli amalga oshirildi")
    
    
@trades_router.post("/take_product_to_pre_order_r")
def take_product_to_pre_order_r(new_trade: Trade_pr_to_pre_order, db: Session = ActiveSession, current_user: NewUser = Depends(get_current_active_user)):
    if current_user.role not in ["seller", "seller_admin"] :
        raise HTTPException(status_code = 400, detail = "Sizga ruhsat berilmagan")
    if take_product_to_pre_order(new_trade, current_user, db) :
        raise HTTPException(status_code = 200, detail = "Amaliyot muvaffaqiyatli amalga oshirildi")
    
    
@trades_router.delete("/delete_product_from_pre_order_r/{id}")
def delete_product_from_pre_order_r(id: int, db: Session = ActiveSession, current_user: NewUser = Depends(get_current_active_user)):
    if current_user.role not in ["seller", "seller_admin"] :
        raise HTTPException(status_code = 400, detail = "Sizga ruhsat berilmagan")
    if delete_product_from_pre_order(id, db, current_user) :
        raise HTTPException(status_code = 200, detail = "Amaliyot muvaffaqiyatli amalga oshirildi")
    
    
@trades_router.post("/take_component_item_to_pre_order_r")
def take_component_item_to_pre_order_r(new_trade: Trade_comp_item_to_pre_order, db: Session = ActiveSession, current_user: NewUser = Depends(get_current_active_user)):
    if current_user.role not in ["seller", "seller_admin"] :
        raise HTTPException(status_code = 400, detail = "Sizga ruhsat berilmagan")
    if take_component_item_to_pre_order(new_trade, current_user, db) :
        raise HTTPException(status_code = 200, detail = "Amaliyot muvaffaqiyatli amalga oshirildi")
    
    
@trades_router.delete("/delete_component_item_from_pre_order_r/{id}")
def delete_component_item_from_pre_order_r(id: int, db: Session = ActiveSession, current_user: NewUser = Depends(get_current_active_user)):
    if current_user.role not in ["seller", "seller_admin"] :
        raise HTTPException(status_code = 400, detail = "Sizga ruhsat berilmagan")
    if delete_component_item_from_pre_order(id, db, current_user) :
        raise HTTPException(status_code = 200, detail = "Amaliyot muvaffaqiyatli amalga oshirildi")