import math
from sqlalchemy import or_
from sqlalchemy.orm import joinedload, Session
from fastapi import HTTPException
from ..models.product_type import *
from ..models.product_store import *
from ..models.product_cycle import *
from ..models.cycle import *
from ..models.cycle_store import *
from ..models.plant_cycle import *
from ..models.plant_user import *
from ..models.plan import *
from developers.yusufjon.utils.trlatin import tarjima


def get_all_product_types(disabled, plant_id, warehouse, search, page, limit, usr, db: Session):
    if page == 1 or page < 1:
        offset = 0
    else:
        offset = (page-1) * limit

    product_types = db.query(Product_Type).filter(Product_Type.disabled == disabled).options(
        joinedload(Product_Type.olchov)
    )

    if usr.role == 'plant_admin' or plant_id > 0:

        pids = []
        if plant_id > 0:
            pids.append(plant_id)
        else:
            for one in db.query(Plant_User).filter_by(user_id=usr.id, disabled=False, admin=True):
                pids.append(one.plant_id)

        product_types = product_types\
            .join(Product_Type.products)\
            .join(Product.product_cycles)\
            .join(Product_Cycle.cycle)\
            .filter(Cycle.disabled == False, Cycle.plant_cycles.any(Plant_Cycle.plant_id.in_(pids)))

    if warehouse == 'product_store':
        if usr.role != 'plant_admin':
            product_types = product_types.join(Product_Type.products)

        product_types = product_types\
            .join(Product.product_stores)\
            .filter(Product_Store.market_id == 0, Product_Store.value > 0)

    if warehouse == 'cycle_store':

        if usr.role != 'plant_admin':
            product_types = product_types.join(Product_Type.products)

        product_types = product_types\
            .join(Product.cycle_stores)\
            .filter(Cycle_Store.value > 0)
    
    if warehouse == 'plan':

        product_types = db.query(Product_Type).select_from(Plan)\
            .join(Plan.product)\
            .join(Product.product_type)\
            .filter(Plan.rest_value > 0, Plan.disabled==False).group_by(Product_Type.id)




    if search:
        product_types = product_types.filter(
            or_(
                Product_Type.name.like(f"%{tarjima(search, 'uz')}%"),
                Product_Type.name.like(f"%{tarjima(search, 'ru')}%"),
            )
        )

    all_data = product_types.order_by(
        Product_Type.number.asc()).offset(offset).limit(limit)
    count_data = product_types.count()

    return {
        "data": all_data.all(),
        "page_count": math.ceil(count_data / limit),
        "data_count": count_data,
        "current_page": page,
        "page_limit": limit,
    }


def create_product_type(form_data, usr, db):

    new_product_type = Product_Type(
        name=form_data.name,
        status=form_data.status,
        image=form_data.image,
        filial_id=form_data.filial_id,
        olchov_id=form_data.olchov_id,
        detail=form_data.detail
    )

    db.add(new_product_type)
    db.commit()

    raise HTTPException(status_code=200, detail="Ma`lumotlar saqlandi!")


def update_product_type(id, form_data, usr, db):
    product_type = db.query(Product_Type).filter(Product_Type.id == id)
    this_product_type = product_type.first()
    if this_product_type:
        product_type.update({
            Product_Type.name: form_data.name,
            Product_Type.status: form_data.status,
            Product_Type.image: form_data.image,
            Product_Type.filial_id: form_data.filial_id,
            Product_Type.olchov_id: form_data.olchov_id,
        })
        db.commit()

        raise HTTPException(status_code=200, detail="O`zgarish saqlandi!")
    else:
        raise HTTPException(status_code=400, detail="So`rovda xatolik!")
