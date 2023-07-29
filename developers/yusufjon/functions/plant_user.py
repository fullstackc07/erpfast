import math
from sqlalchemy import or_
from sqlalchemy.orm import joinedload, Session
from fastapi import HTTPException
from developers.yusufjon.models.plant_user import *
from developers.yusufjon.utils.trlatin import tarjima


def get_all_plant_users(plant_id, disabled, search, page, limit, usr, db):
    if page == 1 or page < 1:
        offset = 0
    else:
        offset = (page-1) * limit

    plant_users = db.query(Plant_User).options(
        joinedload(Plant_User.user).subqueryload(User.shift),
    ).join(Plant_User.user).filter(Plant_User.disabled == disabled)

    if plant_id > 0:
        plant_users = plant_users.filter(Plant_User.plant_id == plant_id)

    if search:
        plant_users = plant_users.filter(
            or_(
                User.name.like(f"%{tarjima(search, 'ru')}%"),
                User.name.like(f"%{tarjima(search, 'uz')}%"),
            )
        )

    all_data = plant_users.order_by(
        Plant_User.id.desc()).offset(offset).limit(limit)
    count_data = plant_users.count()

    return {
        "data": all_data.all(),
        "page_count": math.ceil(count_data / limit),
        "data_count": count_data,
        "current_page": page,
        "page_limit": limit,
    }


def create_plant_user(form_data, usr, db):
    new_plant_user = Plant_User(
        plant_id=form_data.plant_id,
        user_id=form_data.user_id,
        admin=form_data.admin,
        disabled=form_data.disabled,
    )

    db.add(new_plant_user)
    db.commit()

    raise HTTPException(status_code=200, detail="Ma`lumotlar saqlandi!")


def update_plant_user(id, form_data, usr, db):
    plant_user = db.query(Plant_User).filter(Plant_User.id == id)
    this_plant_user = plant_user.first()
    if this_plant_user:
        plant_user.update({
            Plant_User.plant_id: form_data.plant_id,
            Plant_User.user_id: form_data.user_id,
            Plant_User.admin: form_data.admin,
            Plant_User.disabled: form_data.disabled,
        })
        db.commit()

        raise HTTPException(status_code=200, detail="O`zgarish saqlandi!")
    else:
        raise HTTPException(status_code=400, detail="So`rovda xatolik!")
