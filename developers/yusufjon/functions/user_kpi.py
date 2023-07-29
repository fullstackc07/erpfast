import math
from sqlalchemy.orm import joinedload, Session
from fastapi import HTTPException
from developers.yusufjon.models.user_kpi import *
from developers.yusufjon.utils.trlatin import *
from sqlalchemy import or_

def get_all_user_kpis(user_id, cycle_id, disabled, search, page, limit, usr, db: Session):

    if page == 1 or page < 1:
        offset = 0
    else:
        offset = (page-1) * limit

    user_kpis = db.query(User_Kpi).filter(User_Kpi.disabled==disabled)
    
    
    if cycle_id > 0:
        user_kpis = user_kpis.filter(User_Kpi.cycle_id==cycle_id).options(joinedload(User_Kpi.user).load_only(User.name))

    if user_id > 0:
        user_kpis = user_kpis.filter(User_Kpi.user_id==user_id).options(joinedload(User_Kpi.cycle))



    if search:
        user_kpis = user_kpis.join(
        User_Kpi.cycle).join(
        User_Kpi.user).filter(
            or_(
                Cycle.name.like(f"%{tarjima(search, 'ru')}%"),
                Cycle.name.like(f"%{tarjima(search, 'uz')}%"),
                User.name.like(f"%{tarjima(search, 'ru')}%"),
                User.name.like(f"%{tarjima(search, 'uz')}%"),
            )
        )

    all_data = user_kpis.order_by(
        User_Kpi.id.desc()).offset(offset).limit(limit)
    count_data = user_kpis.count()

    return {
        "data": all_data.all(),
        "page_count": math.ceil(count_data / limit),
        "data_count": count_data,
        "current_page": page,
        "page_limit": limit,
    }


def create_user_kpi(form_data, usr, db):
    new_user_kpi = User_Kpi(
        user_id=form_data.user_id,
        cycle_id=form_data.cycle_id,
        value=form_data.value,
    )

    db.add(new_user_kpi)
    db.commit()

    raise HTTPException(status_code=200, detail="Ma`lumotlar saqlandi!")


def update_user_kpi(id, form_data, usr, db):
    user_kpi = db.query(User_Kpi).filter(User_Kpi.id == id)
    this_user_kpi = user_kpi.first()
    if this_user_kpi:
        user_kpi.update({
            User_Kpi.user_id: form_data.user_id,
            User_Kpi.cycle_id: form_data.cycle_id,
            User_Kpi.value: form_data.value,
            User_Kpi.disabled: form_data.disabled,
        })
        db.commit()

        raise HTTPException(status_code=200, detail="O`zgarish saqlandi!")
    else:
        raise HTTPException(status_code=400, detail="So`rovda xatolik!")
