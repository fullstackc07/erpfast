from fastapi import HTTPException, APIRouter, Depends
from typing import Optional, List
from developers.yusufjon.schemas.user import NewUser
from security.auth import get_current_active_user
from databases.main import ActiveSession
from sqlalchemy.orm import joinedload, Session
from sqlalchemy.sql import or_, and_
from developers.yusufjon.models.product_transfer import *
from developers.yusufjon.models.material_store import *
from developers.yusufjon.functions.product_transfer import *
from developers.yusufjon.schemas.product_transfer import *

product_transfer_router = APIRouter(tags=['Product_Transfer Endpoint'])


@product_transfer_router.get("/product_transfers", description="This router returns list of the product_transfers using pagination")
async def get_product_transfers_list(
    market_id: int,
    search: Optional[str] = "",
    page: int = 1,
    limit: int = 10,
    db: Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if not usr.role in ['any_role']:
        return get_all_product_transfers(search, market_id, page, limit, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")


@product_transfer_router.post("/product_transfer/create", description="This router is able to add new product_transfer")
async def create_new_product_transfer(
    form_data: NewProduct_Transfer,
    db: Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst', 'plant_admin', 'seller', 'seller_admin']:
        return create_product_transfer(form_data, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")


@product_transfer_router.get("/product_transfer_acceptance/{market_id}")
async def update_one_product_transfer(
    market_id: Optional[int] = 0,
    toMarket: Optional[bool] = True,
    db: Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if not usr.role in ['any_role']:

        if usr.role in ['seller', 'seller_admin']:
            market_id = usr.market_id

        if market_id > 0:
            ffilter = Product_Store.market_id == market_id
        else:
            ffilter = Product_Store.market_id > 0

        return db.query(Product_Transfer).options(
            joinedload(Product_Transfer.product).subqueryload(Product.olchov),
            joinedload(Product_Transfer.material)
        ).filter(ffilter).filter_by(took_user_id=0, toMarket=toMarket).all()

    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")


@product_transfer_router.put("/product_transfer_acceptance")
async def update_one_product_transfer(
    ids: List[int],
    toMarket: Optional[bool] = True,
    db: Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst', 'plant_admin', 'seller', 'seller_admin']:
        for id in ids:

            product_transfer = db.query(Product_Transfer).filter_by(
                id=id, toMarket=toMarket)
            this_product_transfer = product_transfer.first()

            if this_product_transfer:
                product_store = db.query(Product_Store).filter(
                    Product_Store.product_id == this_product_transfer.product_id,
                    Product_Store.size1 == this_product_transfer.size1,
                    Product_Store.size2 == this_product_transfer.size2,
                    Product_Store.trade_id == 0,
                    Product_Store.market_id == (
                        this_product_transfer.market_id if toMarket == True else 0),
                    Product_Store.price == this_product_transfer.cost,
                    Product_Store.material_id == this_product_transfer.material_id,
                )

                this_product_store = product_store.first()

                if this_product_store:
                    product_store.update({
                        Product_Store.value: Product_Store.value + this_product_transfer.value
                    })
                else:
                    db.add(Product_Store(
                        product_id=this_product_transfer.product_id,
                        size1=this_product_transfer.size1,
                        size2=this_product_transfer.size2,
                        material_id=this_product_transfer.material_id,
                        trade_id=0,
                        market_id=(
                            this_product_transfer.market_id if toMarket == True else 0),
                        price=this_product_transfer.cost,
                        value=this_product_transfer.value,
                    ))

            product_transfer.update({Product_Transfer.took_user_id: usr.id})

        db.commit()

        return 'success'

    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")


@product_transfer_router.put("/product_transfer_cancellation")
async def cancel_product_transfers(
    ids: List[int],
    toMarket: Optional[bool] = True,
    db: Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst', 'plant_admin', 'seller', 'seller_admin']:
        for id in ids:

            product_transfer = db.query(Product_Transfer).filter_by(
                id=id, toMarket=toMarket)
            this_product_transfer = product_transfer.first()

            if this_product_transfer:
                product_store = db.query(Product_Store).filter(
                    Product_Store.product_id == this_product_transfer.product_id,
                    Product_Store.size1 == this_product_transfer.size1,
                    Product_Store.size2 == this_product_transfer.size2,
                    Product_Store.trade_id == 0,
                    Product_Store.market_id == (
                        0 if toMarket == True else this_product_transfer.market_id),
                    Product_Store.price == this_product_transfer.cost,
                    Product_Store.material_id == this_product_transfer.material_id,
                )

                this_product_store = product_store.first()

                if this_product_store:
                    product_store.update({
                        Product_Store.value: Product_Store.value + this_product_transfer.value
                    })
                else:
                    db.add(Product_Store(
                        product_id=this_product_transfer.product_id,
                        size1=this_product_transfer.size1,
                        size2=this_product_transfer.size2,
                        material_id=this_product_transfer.material_id,
                        trade_id=0,
                        market_id=(
                            0 if toMarket == True else this_product_transfer.market_id),
                        price=this_product_transfer.cost,
                        value=this_product_transfer.value,
                    ))

            product_transfer.delete()

        db.commit()

        return 'success'

    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")


@product_transfer_router.get("/available_quantity")
async def get_available_quantity(
    trade_item_id: int,
    db: Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst', 'plant_admin', 'seller', 'seller_admin']:

        trade_item: Trade_items = db.query(Trade_items).get(trade_item_id)

        if trade_item:
            if len(trade_item.trade_items_size) > 0:
                size1 = trade_item.trade_items_size[0].size1
                size2 = trade_item.trade_items_size[0].size2
            else:
                size1 = 0
                size2 = 0

        if trade_item.component_item.product_id > 0:

            # return trade_item.component_item.product_id

            return db.query(func.coalesce(func.sum(Product_Store.value), 0)).filter(
                
                and_(
                    Product_Store.material_id == trade_item.material_id,
                    Product_Store.size1 == size1,
                    Product_Store.size2 == size2,
                    Product_Store.trade_id == 0,
                    Product_Store.trade_item_id == 0,
                    Product_Store.value > 0,
                    Product_Store.product_id == trade_item.component_item.product_id,
                    or_(
                        Product_Store.market_id == usr.market_id,
                        Product_Store.market_id == 0,
                    ),
                )
            ).scalar()
        else:
            return 0

    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")


class Reclamation(BaseModel):
    trade_item_id: int
    value: float


@product_transfer_router.post("/reclamation_trade_item")
async def post_reclamation_trade_item(
    form_data: Reclamation,
    db: Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst', 'plant_admin', 'seller', 'seller_admin']:

        trade_item: Trade_items = db.query(
            Trade_items).get(form_data.trade_item_id)

        if trade_item:
            if len(trade_item.trade_items_size) > 0:
                size1 = trade_item.trade_items_size[0].size1
                size2 = trade_item.trade_items_size[0].size2
            else:
                size1 = 0
                size2 = 0

        if trade_item.component_item.product_id > 0:

            values = db.query(Product_Store).filter(
                or_(
                    Product_Store.market_id == usr.market_id,
                    Product_Store.market_id == 0,
                ),
                Product_Store.material_id == trade_item.material_id,
                Product_Store.product_id == trade_item.component_item.product_id,
                Product_Store.size1 == size1,
                Product_Store.size2 == size2,
                Product_Store.trade_id == 0,
                Product_Store.trade_item_id == 0,
                Product_Store.value > 0
            ).all()
            needy_value = form_data.value
            for pr_store in values:
                if needy_value > 0:
                    if pr_store.value <= needy_value:
                        needy_value -= pr_store.value

                        trade_item_price = trade_item.price

                        db.query(Product_Store).filter_by(id=pr_store.id).update(
                            {Product_Store.trade_id: trade_item.trade_id, Product_Store.trade_item_id: trade_item.id, Product_Store.price: trade_item_price})
                    else:
                        db.query(Product_Store).filter_by(id=pr_store.id).update(
                            {Product_Store.value: Product_Store.value - needy_value})
                        db.add(Product_Store(
                            product_id=pr_store.product_id,
                            value=needy_value,
                            price=pr_store.price,
                            trade_price=trade_item.price,
                            trade_id=trade_item.trade_id,
                            trade_item_id=trade_item.id,
                            size1=size1,
                            size2=size2,
                            material_id=trade_item.material_id
                        ))
                        needy_value = 0
                else:
                    break

            if needy_value:
                raise HTTPException(
                    status_code=400, detail='Mahsulot yetarli emas!')
            else:
                db.commit()
                return 'success'
        else:
            return 0

    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")
