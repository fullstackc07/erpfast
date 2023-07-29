from fastapi import HTTPException, APIRouter, Depends
from typing import Optional
from developers.yusufjon.schemas.user import NewUser
from security.auth import get_current_active_user
from databases.main import ActiveSession
from sqlalchemy.orm import joinedload, Session
from developers.yusufjon.models.supplier import *
from developers.yusufjon.functions.supplier import *
from developers.yusufjon.schemas.supplier import *

supplier_router = APIRouter(tags=['Supplier Endpoint'])

@supplier_router.get("/suppliers", description="This router returns list of the suppliers using pagination")
async def get_suppliers_list(
    search: Optional[str] = "",
    page: int = 1,
    limit: int = 10,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):   
    if usr.role in ['admin', 'accountant', 'analyst', 'plant_admin']:
        return get_all_suppliers(search, page, limit, usr, db)  
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")  



@supplier_router.get("/supplier_one", description="This router returns list of the suppliers using pagination")
async def get_suppliers_list(
    id: int,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):   
    if usr.role in ['admin', 'accountant', 'analyst', 'plant_admin']:
        supplier = db.query(Supplier).filter_by(id=id).options(
            joinedload(Supplier.phones).load_only(Phone.number)
        ).filter(Supplier.id == id).first()
    
        if supplier:
            return supplier
        else:
            raise HTTPException(status_code=400, detail="So`rovda xatolik!")
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!") 

@supplier_router.post("/supplier/create", description="This router is able to add new supplier")
async def create_new_supplier(
    form_data: NewSupplier,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst', 'plant_admin']:
        return create_supplier(form_data, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")

@supplier_router.put("/supplier/{id}/update", description="This router is able to update supplier")
async def update_one_supplier(
    id: int,
    form_data: UpdateSupplier,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst', 'plant_admin']:
        
        return update_supplier(id, form_data, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")
