from fastapi import HTTPException, APIRouter, Depends
from typing import Optional
from developers.yusufjon.schemas.user import NewUser
from security.auth import get_current_active_user
from databases.main import ActiveSession
from sqlalchemy.orm import Session, joinedload
from developers.yusufjon.models.cycle_store import Cycle_Store
from developers.yusufjon.models.product import Product
from developers.yusufjon.models.cycle import Cycle
from developers.yusufjon.models.plant_user import *
from developers.yusufjon.models.plant import Plant
from developers.yusufjon.models.product_store import Product_Store
from developers.yusufjon.models.product_acceptance import Product_Acceptance
from developers.abdusamad.models import Trades, Orders


warehouse_router = APIRouter(tags=['Warehouse Endpoint'])

@warehouse_router.get("/in_cycle_products")
async def get_ready_products_list(
    product_type_id: int,
    db: Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if not usr.role in ['any_role']:

        return db.query(Cycle_Store, func.coalesce(func.sum(Cycle_Store.value), 0).label("sum_quantity")).options(
            joinedload(Cycle_Store.product).load_only(
                Product.name, Product.image),
            joinedload(Cycle_Store.olchov),
            joinedload(Cycle_Store.material),
            joinedload(Cycle_Store.cycle).load_only(Cycle.name),
        ).join(Cycle_Store.product).filter(Product.product_type_id==product_type_id,Cycle_Store.value > 0)\
        .group_by(Cycle_Store.product_id, Cycle_Store.size1, Cycle_Store.size2, Cycle_Store.material_id).all()
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")


@warehouse_router.get("/ready_products", description="This router returns list of the warehouses using pagination")
async def get_ready_products_list(
    search: Optional[str] = "",
    page: int = 1,
    limit: int = 10,
    db: Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if not usr.role in ['any_role']:

        return db.query(Cycle_Store).filter(
            Cycle_Store.value > 0,
            Cycle_Store.finished == True,
        ).options(
            joinedload(Cycle_Store.product).load_only(
                Product.name, Product.image),
            joinedload(Cycle_Store.olchov),
            joinedload(Cycle_Store.plant).load_only(Plant.name),
            joinedload(Cycle_Store.cycle).load_only(Cycle.name),
            joinedload(Cycle_Store.trade).subqueryload(
                Trades.order).subqueryload(Orders.customer)
        ).group_by(Cycle_Store.trade_id).all()

    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")


@warehouse_router.post("/accept_ready_product")
async def get_ready_products_warehouse(
    id: int, db: Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if not usr.role in ['any_role']:
        cycle_store = db.query(Cycle_Store).filter_by(id=id)
        cycle_store_one = cycle_store.first()


        if cycle_store_one:
            new_product_acceptance = Product_Acceptance(
                cycle_store_id=id,
                user_id=usr.id,
                product_id=cycle_store_one.product_id,
                plant_id=cycle_store_one.plant_id,
                value=cycle_store_one.value
            )
            
            db.add(new_product_acceptance)

            product_store = db.query(Product_Store).filter_by(
                product_id=cycle_store_one.product_id,
                price=cycle_store_one.price,
                trade_id=cycle_store_one.trade_id,
                trade_item_id=cycle_store_one.trade_item_id,
            )

            product_store_one = product_store.first()

            
            if product_store_one:
                
                product_store.update(
                    {Product_Store.value: Product_Store.value + cycle_store_one.value})
            else:
                new_product_store = Product_Store(
                    product_id=cycle_store_one.product_id,
                    price=cycle_store_one.price,
                    trade_id=cycle_store_one.trade_id,
                    trade_item_id=cycle_store_one.trade_item_id,
                    value=cycle_store_one.value
                )
                db.add(new_product_store)

            cycle_store.delete()

            db.commit()

            raise HTTPException(status_code=200, detail=f"Ma'lumotlar salandi")
        else:
            raise HTTPException(status_code=400, detail="So'rovda xatolik!")

    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")
