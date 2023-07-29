import math
from sqlalchemy.orm import joinedload, Session
from fastapi import HTTPException
from developers.yusufjon.models.product_material import *


def product_material_gets(material_id, product_id, page, limit, usr, db):
    if page == 1 or page < 1:
        offset = 0
    else:
        offset = (page-1) * limit

    p_m = db.query(ProductMaterial)

    if not product_id:
        product_id = 0

    if not material_id:
        material_id = 0

    if product_id > 0 and material_id == 0:
        p_m = p_m.filter(ProductMaterial.product_id == product_id)
    elif material_id > 0 and product_id == 0:
        p_m = p_m.filter(ProductMaterial.material_id == material_id)
    elif material_id > 0 and product_id > 0:
        p_m = p_m.filter(ProductMaterial.material_id == material_id).filter(
            ProductMaterial.product_id == product_id)
    else:
        pass

    all_data = p_m.order_by(ProductMaterial.id.desc()).offset(
        offset).limit(limit).all()

    all_data = p_m
    count_data = p_m.count()

    return {
        "data": all_data.all(),
        "page_count": math.ceil(count_data / limit),
        "data_count": count_data,
        "current_page": page,
        "page_limit": limit,
    }


def product_material_insert(data, usr, db):
    if data.type == 'PRODUCT':
        for item in data.values:
            count = db.query(ProductMaterial).filter(ProductMaterial.material_id == item).filter(ProductMaterial.product_id == data.id).count()
            if count <= 0:
                model = ProductMaterial(
                    product_id=data.id,
                    material_id=item,
                )
                db.add(model)
                db.commit()
    if data.type == 'MATERIAL':
        for item in data.values:
            count = db.query(ProductMaterial).filter(ProductMaterial.material_id == data.id).filter(ProductMaterial.product_id == item).count()
            if count <= 0:
                model = ProductMaterial(
                    material_id=data.id,
                    product_id=item,
                )
                db.add(model)
                db.commit()

    raise HTTPException(status_code=200, detail="Ma`lumotlar saqlandi!")

def product_material_delete(id, usr, db):
    model = db.query(ProductMaterial).filter(ProductMaterial.id == id)
    if model.count() > 0:
        db.delete(model.first())
        db.commit()
        raise HTTPException(status_code=200, detail="Ma`lumot o`chirildi!")
    else:
        raise HTTPException(status_code=200, detail="Ma`lumotlar yo`q!")
