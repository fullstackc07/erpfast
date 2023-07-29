import math
from sqlalchemy.orm import joinedload, Session
from fastapi import HTTPException
from developers.yusufjon.models.product_transfer import *
from developers.yusufjon.models.product_store import *
from developers.yusufjon.schemas.product_transfer import *


def get_all_product_transfers(search, market_id, page, limit, usr, db: Session):

    if page == 1 or page < 1:
        offset = 0
    else:
        offset = (page-1) * limit

    product_transfers = db.query(Product_Transfer)\
        .options(
        joinedload(Product_Transfer.product).subqueryload(Product.olchov),
        joinedload(Product_Transfer.user).load_only(User.name),
        joinedload(Product_Transfer.took_user).load_only(User.name),
    )\
        .join(Product_Transfer.product)\
        .filter(Product_Store.market_id == market_id)

    if search:
        product_transfers = product_transfers.filter(
            Product.name.like(f"%{search}%"),
        )

    all_data = product_transfers.order_by(
        Product_Transfer.id.desc()).offset(offset).limit(limit)
    count_data = product_transfers.count()

    return {
        "data": all_data.all(),
        "page_count": math.ceil(count_data / limit),
        "data_count": count_data,
        "current_page": page,
        "page_limit": limit,
    }


def create_product_transfer(form_data: NewProduct_Transfer, usr, db: Session):


    product = db.query(Product).filter_by(id=form_data.product_id).first()

    if product:

        product_stores = db.query(Product_Store).filter(
            Product_Store.product_id == form_data.product_id,
            Product_Store.trade_id == 0,
            Product_Store.material_id == form_data.material_id,
            Product_Store.size1 == form_data.size1,
            Product_Store.size2 == form_data.size2,
            Product_Store.market_id == (0 if form_data.tomarket == True else form_data.market_id)
        )
        
        if product.product_type.hasSize:
            product_store = product_store.filter(Product_Store.size1 == form_data.size1, Product_Store.size2 == form_data.size2,)

        needy_value = form_data.value

        for product_store in product_stores.all():
            if needy_value > 0:
                cost = product_store.price
                if product_store.value < needy_value:
                    needy_value = needy_value - product_store.value
                    db.query(Product_Store).filter_by(
                        id=product_store.id).update({Product_Store.value: 0})
                else:
                    db.query(Product_Store).filter_by(id=product_store.id).update(
                        {Product_Store.value: Product_Store.value - needy_value})
                    needy_value = 0
            else:
                break

            # kerakli mahsulotlar omborda yetarlimi tekshirish
        if needy_value > 0:
            raise HTTPException(
                status_code=400, detail='Yetarli emas!')

        new_product_transfer = Product_Transfer(
            product_id=form_data.product_id,
            user_id=usr.id,
            market_id=form_data.market_id,
            value=form_data.value,
            cost=cost,
            toMarket=form_data.tomarket,
            size1=form_data.size1,
            size2=form_data.size2,
            material_id=form_data.material_id,
        )

        db.add(new_product_transfer)
        db.commit()

        raise HTTPException(status_code=200, detail="Ma`lumotlar saqlandi!")

# def update_product_transfer(id, form_data: UpdateProduct_Transfer, usr, db: Session):
#     product_transfer = db.query(Product_Transfer).filter(Product_Transfer.id == id)
#     this_product_transfer = product_transfer.first()
#     if this_product_transfer:
#         product_transfer.update({
#             Product_Transfer.product_id: form_data.product_id,
#             Product_Transfer.user_id: form_data.user_id,
#             Product_Transfer.market_id: form_data.market_id,
#             Product_Transfer.datetime: form_data.datetime,
#             Product_Transfer.value: form_data.value,
#             Product_Transfer.toMarket: form_data.tomarket,
#         })
#         db.commit()

#         raise HTTPException(status_code=200, detail="O`zgarish saqlandi!")
#     else:
#         raise HTTPException(status_code=400, detail="So`rovda xatolik!")
