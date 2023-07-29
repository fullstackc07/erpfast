from datetime import timedelta
import math
import datetime
from sqlalchemy import Interval, bindparam, or_, func, text
from sqlalchemy.orm import joinedload, Session
from fastapi import HTTPException
from developers.yusufjon.models.utilization import *


def get_all_utilization(type, page, limit, usr, db):

    if page == 1 or page < 1:
        offset = 0
    else:
        offset = (page-1) * limit
    
    utilization = db.query(Utilization)

    if len(type) > 0:
        utilization = utilization.filter(
            or_(
                Utilization.type.like(f"%{search}%"),
            )
        )

    all_data = utilization.order_by(Utilization.id.asc()).offset(offset).limit(limit)
    count_data = utilization.count()

    return {
        "data": all_data.all(),
        "page_count": math.ceil(count_data / limit),
        "data_count": count_data,
        "current_page": page,
        "page_limit": limit,
    }


def create_new_utilization(form_data, usr, db):

    new_utilization = Utilization(
        item_id=form_data.product_id,
        type=form_data.type,
        user_id=usr.id,
        datetime=func.now(),
        value=form_data.value,
        plant_id=form_data.plant_id
    )

    db.add(new_utilization)
    db.commit()

    raise HTTPException(status_code=200, detail="Ma`lumotlar saqlandi!")

def update_utilization(id,form_data, usr, db:Session):
    utilization = db.query(Utilization).filter_by(id=id)
    this_utilization = utilization.first()

    if this_utilization:
        utilization.update({
            Utilization.item_id: form_data.item_id,
            Utilization.type: form_data.type,
            Utiization.user_id: usr.id,
            Utilization.datetime: func.now(),
            Utilization.value: form_data.value,
            Utilization.plant_id: form_data.plant_id,
            Utilization.cost: form_data.cost
        })
        db.commit()
        raise HTTPException(status_code=200, detail="Ma`lumotlar saqlandi!")
    else:
        raise HTTPException(status_code=400, detail="So`rovda xatolik!")