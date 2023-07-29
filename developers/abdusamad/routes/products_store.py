from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from security.auth import get_current_active_user
from databases.main import ActiveSession
from developers.yusufjon.schemas.user import NewUser
from ..functions.products_store import *


product_store_router = APIRouter(tags=['Product_Store'])



@product_store_router.get("/get_products_store")
def get_products_store(search: str = None, pr_type_id: int = 0, id: int = 0, market_id: int = 0, size1: int = 0, size2: int = 0, page: int = 1, limit: int = 25, db: Session = ActiveSession, current_user: NewUser = Depends(get_current_active_user)):
    if page <= 0 or limit < 0 :
        raise HTTPException(status_code = 400, detail = "page yoki limit 0 dan kichik kiritilmasligi kerak")

    if id > 0 :
        return one_product_store(id, db)
    
    return all_products_store(search, False, pr_type_id, market_id, size1, size2, page, limit, db)


@product_store_router.get("/get_products_store_trade")
def get_products_store(search: str = None, pr_type_id: int = 0, id: int = 0, market_id: int = 0, size1: int = 0, size2: int = 0, page: int = 1, limit: int = 25, db: Session = ActiveSession, current_user: NewUser = Depends(get_current_active_user)):
    if page <= 0 or limit < 0 :
        raise HTTPException(status_code = 400, detail = "page yoki limit 0 dan kichik kiritilmasligi kerak")
    if current_user.role not in ["admin", "seller", "seller_admin"] :
        raise HTTPException(status_code = 400, detail = "Sizga ruhsat berilmagan")
    if id > 0 :
        return one_product_store(id, db)
    return all_products_store(search, True, pr_type_id, market_id, size1, size2, page, limit, db)