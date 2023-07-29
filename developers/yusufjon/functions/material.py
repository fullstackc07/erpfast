import math
from sqlalchemy import or_
from sqlalchemy.orm import joinedload, Session
from fastapi import HTTPException
from developers.yusufjon.models.material import *
from developers.yusufjon.models.material_type import *

def get_all_materials(material_type_id, search, page, limit, usr, db: Session):
    if page == 1 or page < 1:
        offset = 0
    else:
        offset = (page-1) * limit
    
    materials = db.query(
        Material.id,
        Material.price,
        Material.alarm_value,
        Material.name,
        Material.unit,
        Material.has_volume,
        Olchov.name.label("olchov"),
        Olchov.id.label("olchov_id"),
        Material_Type.name.label("material_type"),
    )\
        .join(Material.material_type)\
        .join(Material.olchov)\

    if material_type_id > 0:
        materials = materials.filter(Material.material_type_id==material_type_id)

    if search:
        materials = materials.filter(
            or_(
                Material.name.like(f"%{search}%"),
                Olchov.name.like(f"%{search}%"),
            )
        )

    all_data = materials.order_by(Material.id.desc()).offset(offset).limit(limit)
    count_data = materials.count()

    return {
        "data": all_data.all(),
        "page_count": math.ceil(count_data / limit),
        "data_count": count_data,
        "current_page": page,
        "page_limit": limit,
    }

def create_material(form_data, usr, db: Session):

    material_type = db.query(Material_Type).filter_by(id=form_data.material_type_id).first()

    if not material_type:
        raise HTTPException(status_code=400, detail="Homashyo turi topilmadi!")

    olchov = db.query(Olchov).filter_by(id=form_data.olchov_id).first()

    if not olchov:
        raise HTTPException(status_code=400, detail="O`lchov birligi topilmadi!")

    unique_name = db.query(Material).filter_by(name=form_data.name, material_type_id=form_data.material_type_id).first()

    if unique_name:
        raise HTTPException(status_code=400, detail="Bu nom band!")

    new_material = Material(
        material_type_id=form_data.material_type_id,
        name=form_data.name,
        unit=form_data.unit,
        has_volume=form_data.has_volume,
        price=form_data.price,
        alarm_value=form_data.alarm_value,
        olchov_id=form_data.olchov_id,
    )

    db.add(new_material)
    db.commit()

    raise HTTPException(status_code=200, detail="Ma`lumotlar saqlandi!")

def update_material(id, form_data, usr, db):
    material = db.query(Material).filter(Material.id == id)
    this_material = material.first()
    if this_material:

        material_type = db.query(Material_Type).filter_by(id=form_data.material_type_id).first()

        if not material_type:
            raise HTTPException(status_code=400, detail="Homashyo turi topilmadi!")

        olchov = db.query(Olchov).filter_by(id=form_data.olchov_id).first()

        if not olchov:
            raise HTTPException(status_code=400, detail="O`lchov birligi topilmadi!")

        unique_name = db.query(Material).filter_by(name=form_data.name, material_type_id=form_data.material_type_id).filter(Material.name != form_data.name).first()

        if unique_name:
            raise HTTPException(status_code=400, detail="Bu nom band!")

        material.update({    
            Material.material_type_id: form_data.material_type_id,
            Material.name: form_data.name,
            Material.unit: form_data.unit,
            Material.alarm_value: form_data.alarm_value,
            Material.has_volume: form_data.has_volume,
            Material.price: form_data.price,
            Material.olchov_id: form_data.olchov_id,
        })
        db.commit()

        raise HTTPException(status_code=200, detail="O`zgarish saqlandi!")
    else:
        raise HTTPException(status_code=400, detail="So`rovda xatolik!")
    
