from fastapi import HTTPException, APIRouter, Depends
from typing import Optional
from developers.yusufjon.schemas.user import NewUser
from security.auth import get_current_active_user
from databases.main import ActiveSession
from sqlalchemy.orm import joinedload, Session
from typing import Optional
from developers.abdusamad.models import Expenses
from developers.yusufjon.functions.expense import *
from datetime import date

expense_router = APIRouter(tags=['Expenses Endpoint'])

@expense_router.get("/expenses", description="This router returns list of the expenses using pagination")
async def get_expenses_list(
    from_time: date = None,
    to_time: date = None,
    kassa_id: Optional[int] = 0,
    type:  Optional[str] = "",
    source: Optional[int] = 0, 
    market_id: Optional[int] = 0,
    page: int = 1,
    limit: int = 10,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):   
    if usr.role in ["admin", "seller", "seller_admin"]:
        return get_expenses(from_time, to_time, kassa_id, type, source, market_id, page, limit, db, usr)  
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")  

"""@expense_router.get("/expenses/test", description="This router returns list of the expenses using pagination")
async def get_expenses_list(
    from_time: date = None,
    to_time: date = None,
    kassa_id: Optional[int] = 0,
    type:  Optional[str] = "",
    source: Optional[int] = 0, 
    market_id: Optional[int] = 0,
    page: int = 1,
    limit: int = 10,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):   
    if usr.role in ["admin", "seller", "seller_admin"]:
        return test_get_expenses(from_time, to_time, kassa_id, type, source, market_id, page, limit, db, usr)  
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!") """