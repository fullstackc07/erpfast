from datetime import datetime
import math
from sqlalchemy.orm import joinedload, Session
from fastapi import HTTPException
from developers.yusufjon.models.norm import *
from developers.yusufjon.models.product import Product
from developers.yusufjon.models.plant import Plant
from developers.yusufjon.models.production import Production
from developers.yusufjon.schemas.norm import *


def get_all_norms(plant_id, page, limit, usr, db: Session):
    if page == 1 or page < 1:
        offset = 0
    else:
        offset = (page-1) * limit

    norms = db.query(Norm).filter(Norm.disabled==False)

    if plant_id > 0:
        norms = norms.filter(Norm.plant_id == plant_id)
    else:
        norms = norms.options(joinedload(Norm.plant).load_only(Plant.name))
    norms = norms.options(joinedload(Norm.olchov))

    all_data = norms.order_by(Norm.id.desc()).offset(offset).limit(limit)
    count_data = norms.count()
    res = []
    for one in all_data.all():
        text = ""
        ids = one.products.split(";")
        idss = []
        for x in ids:
            try:
                idss.append(int(x))
                product = db.query(Product).filter_by(id=x).first()
                if product:
                    text += f"{product.name}, "

            except Exception as e:
                pass
        
        one.products = text
        one.done_value = db.query(func.coalesce(func.sum(Production.value), 0)).filter(
            Production.product_id.in_(idss),
            Production.plant_id==plant_id,
            func.date(Production.created_at) >= datetime.now().strftime("%Y-%m-01")
        ).scalar()
        
        res.append(one)

    return {
        "data": res,
        "page_count": math.ceil(count_data / limit),
        "data_count": count_data,
        "current_page": page,
        "page_limit": limit,
    }


def create_norm(form_data: NewNorm, usr, db: Session):

    ids = form_data.products.split(";")
    idss = []
    for x in ids:
        try:
            idss.append(int(x))
        except Exception as e:
            pass

    if db.query(Product).filter(Product.id.in_(idss), Product.disabled == False).count() != len(idss):
        raise HTTPException(
            status_code=400,  detail="Noto'gri mahsulot tanlandi!")

    new_norm = Norm(
        products=form_data.products,
        value=form_data.value,
        plant_id=form_data.plant_id,
        olchov_id=form_data.olchov_id,
    )

    db.add(new_norm)
    db.commit()

    raise HTTPException(status_code=200, detail="Ma`lumotlar saqlandi!")


def update_norm(id, form_data: UpdateNorm, usr, db: Session):
    norm = db.query(Norm).filter(Norm.id == id)
    this_norm = norm.first()
    if this_norm:

        ids = form_data.products.split(";")
        idss = []
        for x in ids:
            try:
                idss.append(int(x))
            except Exception as e:
                pass

        if db.query(Product).filter(Product.id.in_(idss), Product.disabled == False, Product.olchov_id == form_data.olchov_id).count() != len(idss):
            raise HTTPException(
                status_code=400,  detail="Noto'gri mahsulot tanlandi!")

        norm.update({
            Norm.products: form_data.products,
            Norm.value: form_data.value,
            Norm.plant_id: form_data.plant_id,
            Norm.olchov_id: form_data.olchov_id,
            Norm.disabled: form_data.disabled,
        })
        db.commit()

        raise HTTPException(status_code=200, detail="O`zgarish saqlandi!")
    else:
        raise HTTPException(status_code=400, detail="So`rovda xatolik!")
