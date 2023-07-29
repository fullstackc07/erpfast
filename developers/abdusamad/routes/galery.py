from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from sqlalchemy.orm import Session
from security.auth import get_current_active_user
from databases.main import ActiveSession
from developers.yusufjon.schemas.user import NewUser
from ..functions.galery import *


galery_router = APIRouter(tags=['Galery'])


@galery_router.get("/get_galery")
def get_galery(market_id: int = 0, db: Session = ActiveSession, current_user: NewUser = Depends(get_current_active_user)):
    if current_user.role not in ["admin", "seller", "seller_admin"] :
        raise HTTPException(status_code = 400, detail = "Sizga ruhsat berilmagan")
    return all_galery_files(market_id, db)
    
    
@galery_router.post("/create_galery_file_r")
def create_galery_file_r(file: UploadFile = File(...), comment: str = Form(...), db: Session = ActiveSession, current_user: NewUser = Depends(get_current_active_user)):
    if current_user.role not in ["seller", "seller_admin"] :
        raise HTTPException(status_code = 400, detail = "Sizga ruhsat berilmagan")
    if create_galery_file(file, comment, current_user, db) :
        raise HTTPException(status_code = 200, detail = "Amaliyot muvaffaqiyatli amalga oshirildi")
    
    
@galery_router.delete("/delete_galery_file_r/{id}")
def delete_galery_file_r(id: int, db: Session = ActiveSession, current_user: NewUser = Depends(get_current_active_user)):
    if current_user.role not in ["seller", "seller_admin"] :
        raise HTTPException(status_code = 400, detail = "Sizga ruhsat berilmagan")
    if delete_galery_file(id, db) :
        raise HTTPException(status_code = 200, detail = "Amaliyot muvaffaqiyatli amalga oshirildi")