from fastapi import HTTPException, APIRouter, Depends
from typing import Optional
from developers.yusufjon.schemas.user import NewUser
from security.auth import get_current_active_user
from databases.main import ActiveSession
from sqlalchemy.orm import joinedload, Session
from developers.yusufjon.models.production import *
from developers.yusufjon.functions.production import *
from developers.yusufjon.schemas.production import *
from sqlalchemy.sql import label, or_, and_


production_router = APIRouter(tags=['Production Endpoint'])

@production_router.get("/productions", description="This router returns list of the productions using pagination")
async def get_productions_list(
    plant_id: int = 0,
    search: Optional[str] = "",
    page: int = 1,
    limit: int = 10,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):   
    if usr.role in ['admin', 'accountant', 'analyst', 'plant_admin']:
        return get_all_productions(plant_id, search, page, limit, usr, db)  
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")  

@production_router.get("/production/orders")
async def get_production_orders_list(
    search: Optional[str] = "",
    page: int = 1,
    plant_id: int = 0,
    limit: int = 10,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):   
    if usr.role in ['admin', 'accountant', 'analyst', 'plant_admin']:
        return get_production_orders(search, plant_id, page, limit, usr, db)  
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")


@production_router.get("/production/details")
async def get_production_details(
    product_cycle_id: int,
    plant_id: int,
    material_id: int,
    plan_id: int,
    trade_id: Optional[int] = 1,
    value: Optional[float] = 1,
    size1: Optional[float] = 0,
    size2: Optional[float] = 0,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst', 'plant_admin']:
        return get_production_order_details(plan_id, material_id, size1, size2, plant_id, product_cycle_id, value, trade_id, usr, db)  
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")
    
@production_router.post("/production/create", description="This router is able to add new production")
async def create_new_production(
    form_data: NewProduction,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst', 'plant_admin']:
        await create_production(form_data, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")

@production_router.put("/production/{id}/update", description="This router is able to update production")
async def update_one_production(
    id: int,
    form_data: UpdateProduction,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst', 'plant_admin']:
        return update_production(id, form_data, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")
    
@production_router.delete("/production_delete", description="This router is able to update production")
async def delete_one_production(
    id: int,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst', 'plant_admin']:
        return delete_production(id, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")

@production_router.get("/production/cycles")
async def get_production_cycles(
    search: Optional[str] = "",
    page: int = 1,
    plant_id: int = 0,
    limit: int = 10,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst', 'plant_admin']:
        return production_cycles(search, page, plant_id, limit, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")
    

@production_router.get("/production/trade")
async def get_production_trade(
    trade_id: int,
    db: Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
   
   
   
    material_store = db.query(func.coalesce(func.sum(Material_Store.value), 0)).filter_by(material_id=Component_Item.material_id).subquery()
    product_store = db.query(func.coalesce(func.sum(Product_Store.value), 0)).filter_by(product_id=Component_Item.product_id).filter(
        or_(
            and_(Product_Store.trade_id==trade_id, Product_Store.trade_item_id==Trade_items.id),
            and_(Product_Store.trade_id==0, Product_Store.trade_item_id==0),
        )
    ).subquery()

    details = db.query(
        Trade_items,
        label("warehouse", func.IF(Component_Item.material_id > 0, material_store, product_store)),
        label("needy_value", (Trade_items.quantity*Trades.quantity)),
    ).select_from(Trade_items)\
        .join(Trade_items.trade)\
        .join(Trade_items.component_item)\
        .filter(Trade_items.trade_id==trade_id)\
        .group_by(Trade_items.id).all()

    res = []
    for tr_it in details:

        if tr_it['Trade_items'].component_item.product_id > 0:
            product = tr_it['Trade_items'].component_item.product
            name = product.name
            olchov = product.olchov.name
            image = product.image
        else:
            material = tr_it['Trade_items'].component_item.material
            name = material.name
            olchov = material.olchov.name
            image = ""
        res.append({
            'warehouse': tr_it.warehouse,
            'needy_value': tr_it.needy_value,
            'name': name,
            'olchov': olchov,
            'image': image,

        })

    return res