import math
from typing import Optional
from sqlalchemy.orm import joinedload, Session
from sqlalchemy import func, and_, or_
from fastapi import HTTPException
from developers.yusufjon.models.material_store import *
from developers.yusufjon.models.material_type import *
from developers.yusufjon.schemas.material_store import *
from developers.yusufjon.utils.trlatin import tarjima





def get_all_material_stores(search, material_type_id, plant_id, page, limit, usr, db: Session):
    if page == 1 or page < 1:
        offset = 0
    else:
        offset = (page-1) * limit

    material_stores = db.query(Material_Store).options(
        joinedload(Material_Store.material).subqueryload(Material.material_type),
        joinedload(Material_Store.olchov),
        joinedload(Material_Store.plant),
    )\
        .join(Material_Store.material)\
        .join(Material.material_type)\
        .outerjoin(Material_Store.plant)\
        .join(Material_Store.olchov)\
        .filter(Material_Store.value > 0)
    
    # if plant_id > 0:
    #     material_stores = material_stores.filter(Material_Store.plant_id==plant_id)

    if material_type_id > 0:
        material_stores = material_stores.filter(Material.material_type_id==material_type_id)

    if len(search) > 0:
        material_stores = material_stores.filter(
            or_(
                Material.name.like(f"%{tarjima(search, 'ru')}%"),
                Material.name.like(f"%{tarjima(search, 'uz')}%"),
                Material_Type.name.like(f"%{tarjima(search, 'ru')}%"),
                Material_Type.name.like(f"%{tarjima(search, 'uz')}%"),
                Olchov.name.like(f"%{tarjima(search, 'uz')}%"),
                Olchov.name.like(f"%{tarjima(search, 'uz')}%"),
                Material_Store.value.like(f"%{search}%"),
            )
        )

    
    count_data = material_stores.count()
    all_data = material_stores.group_by(Material_Store.material_id).order_by(Material_Store.id.desc()).offset(offset).limit(limit)
    res = []
    for one_data in all_data.all():
        one_data.value = db.query(func.coalesce(func.sum(Material_Store.value), 0)).filter_by(material_id=one_data.material_id).scalar()
        res.append(one_data)

    return {
        "data": res,
        "page_count": math.ceil(count_data / limit),
        "data_count": count_data,
        "current_page": page,
        "page_limit": limit,
    }


def add_material_store(price, plant_id, material, value, db: Session, commit: Optional[bool] = False):

    material_store = db.query(Material_Store).filter_by(
        plant_id=plant_id,
        material_id=material.id,
    )

    if material_store.first():
        material_store.update({
            Material_Store.value: Material_Store.value + value
        })
    else:
        new_material_store = Material_Store(
            material_id=material.id,
            plant_id=plant_id,
            value=value,
            price=price,
            olchov_id=material.olchov_id,
        )

        db.add(new_material_store)

    if commit:
        db.commit()
    else:
        db.flush()


def substract_material_store(plant_id, value, material, db: Session, commit: Optional[bool] = False):
    
    material_store = db.query(Material_Store).filter(
        Material_Store.plant_id==plant_id,
        Material_Store.material_id==material.id,
        Material_Store.value >= value,
    )

    material_store_one = material_store.first()

    if material_store_one:
        if material_store_one.value >= value:
            material_store.update({
                Material_Store.value: Material_Store.value - value
            })

            if commit:
                db.commit()
            else:
                db.flush()

            return material_store_one.price

    
    raise HTTPException(status_code=400, detail="Homashyo yetarli emas!")
    
   
    