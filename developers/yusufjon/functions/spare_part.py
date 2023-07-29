
from datetime import timedelta, datetime
import math
from sqlalchemy import Interval, bindparam, or_, func, text
from sqlalchemy.orm import joinedload, Session
from fastapi import HTTPException
from ..models.product import *
from ..models.spare_part import *
from ..models.utilization import *
from ..models.product_store import *
from ..models.material import *
from ..models.material_store import *
from ..utils.trlatin import tarjima


def get_all_spare_parts(search, page, limit, usr, db):

    if page == 1 or page < 1:
        offset = 0
    else:
        offset = (page-1) * limit

    spare_parts = db.query(Spare_part).options(
        joinedload(Spare_part.product).subqueryload(Product.product_type),
        joinedload(Spare_part.plant),
        ).join(Spare_part.product)

    if len(search) > 0:
        spare_parts = spare_parts.filter(
            or_(
                Spare_part.machine_name.like(f"%{search}%"),
                Product.name.like(f"%{search}%"),
            )
        )

    all_data = spare_parts.order_by(
        Spare_part.to_date.asc()).offset(offset).limit(limit)
    count_data = spare_parts.count()

    return {
        "data": all_data.all(),
        "page_count": math.ceil(count_data / limit),
        "data_count": count_data,
        "current_page": page,
        "page_limit": limit,
    }


def create_new_spare_part(form_data, usr, db: Session):

    product = db.query(Product).filter(
        Product.id == form_data.product_id).filter_by(disabled=False).first()
    if product:
        new_spare_part = Spare_part(
            machine_name=form_data.machine_name,
            updated_date=form_data.updated_date,
            plant_id=form_data.plant_id,
            to_date=form_data.to_date,
            muddat=func.datediff(form_data.to_date, form_data.updated_date),
            product_id=form_data.product_id
        )

        db.add(new_spare_part)
        db.commit()
        raise HTTPException(status_code=200, detail="Ma`lumotlar saqlandi!")

    else:
        raise HTTPException(
            status_code=400, detail="Bunday mahsulot mavjud emas! Avval mahsulotni qoshin!")


def update_spare_part(id, form_data, usr, db: Session):
    spare_part = db.query(Spare_part).filter(Spare_part.id == id)
    this_spare_part = spare_part.first()

    if this_spare_part:
        spare_part.update({
            Spare_part.machine_name: form_data.machine_name,
            Spare_part.updated_date: form_data.updated_date,
            Spare_part.to_date: form_data.to_date,
            Spare_part.product_id: form_data.product_id,
            Spare_part.plant_id: form_data.plant_id,
        })
        db.commit()
        raise HTTPException(status_code=200, detail="Ma`lumotlar saqlandi!")
    else:
        raise HTTPException(status_code=400, detail="So`rovda xatolik!")


def create_utilization(item_id, type, plant_id, value, usr, db: Session):

    if type == 'product':

        product = db.query(Product).filter_by(
            id=item_id, disabled=False).first()

        if not product:
            raise HTTPException(status_code=400, detail="So`rovda xatolik!")

        product_stores = db.query(Product_Store).filter(
            Product_Store.product_id == item_id,
            Product_Store.trade_id == 0,
            Product_Store.value > 0,
            Product_Store.market_id == 0
        )
        needy_value = value
        for product_store in product_stores:
            if needy_value > 0:
                cost = product_store.price

                if product_store.value < needy_value:

                    db.query(Product_Store).filter_by(id=product_store.id).update({Product_Store.value: 0})\

                    needy_value = needy_value - product_store.value
                else:

                    db.query(Product_Store).filter_by(id=product_store.id).update(
                        {Product_Store.value: Product_Store.value - needy_value})

                    needy_value = 0
            else:
                break

            # kerakli mahsulotlar omborda yetarlimi tekshirish
        if needy_value > 0:
            raise HTTPException(
                status_code=400, detail=product.name + ' yetarli emas!')

    elif type == 'material':
        material = db.query(Material).filter_by(
            id=item_id, disabled=False).first()

        if not material:
            raise HTTPException(status_code=400, detail="So`rovda xatolik!")

        material_stores = db.query(Material_Store).filter(
            Material_Store.material_id == item_id,
            Material_Store.trade_id == 0,
            Material_Store.value > 0,
            Material_Store.market_id == 0
        )
        needy_value = value
        for material_store in material_stores:
            if needy_value > 0:
                cost = material_store.price
                if material_store.value < needy_value:
                    needy_value = needy_value - material_store.value
                    db.query(Material_Store).filter_by(id=material_store.id).update({Material_Store.value: 0})
                else:
                    db.query(Material_Store).filter_by(id=material_store.id).update(
                        {Material_Store.value: Material_Store.value - needy_value})
                    needy_value = 0
            else:
                break

            # kerakli mahsulotlar omborda yetarlimi tekshirish
        if needy_value > 0:
            raise HTTPException(
                status_code=400, detail=material.name + ' yetarli emas!')
    else:
        raise HTTPException(status_code=400, detail="So`rovda xatolik!")

    new_utilization = Utilization(
        item_id=item_id,
        type=type,
        user_id=usr.id,
        value=value,
        plant_id=plant_id,
        cost=cost
    )

    db.add(new_utilization)
    db.commit()

    raise HTTPException(status_code=200, detail="Ma`lumotlar saqlandi!")


def update_new_sparePart(id, value, usr, db):
    spare_part = db.query(Spare_part).filter(Spare_part.id == id)
    this_spare_part = spare_part.first()

    if this_spare_part:

        new_to_date = datetime.now() + timedelta(days=this_spare_part.muddat)

        spare_part.update({
            Spare_part.updated_date: func.now(),
            Spare_part.to_date: new_to_date.strftime("%Y-%m-%d"),
            Spare_part.reminded: False,
        })

        return create_utilization(this_spare_part.product_id, 'product', this_spare_part.plant_id, value, usr, db)

    else:
        raise HTTPException(status_code=400, detail="So`rovda xatolik!")
