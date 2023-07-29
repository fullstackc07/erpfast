import math
from sqlalchemy import or_
from sqlalchemy.orm import joinedload, Session
from fastapi import HTTPException
from developers.yusufjon.models.plant import *
from developers.yusufjon.models.plant_user import Plant_User
from developers.yusufjon.models.shift import Shift
from developers.yusufjon.models.user import User
from developers.yusufjon.schemas.plant import NewPlant, UpdatePlant

def get_all_plants(disabled, search, page, limit, usr, db: Session):
    if page == 1 or page < 1:
        offset = 0
    else:
        offset = (page-1) * limit
    
    plants = db.query(Plant).filter(Plant.disabled==disabled)

    if usr.role == 'plant_admin':
        plants = plants.join(Plant.plant_users).filter(Plant_User.disabled==False, Plant_User.admin==True, Plant_User.user_id==usr.id)

    if search:
        plants = plants.filter(
           Plant.name.like(f"%{search}%"),
        )

    all_data = plants.order_by(Plant.id.desc()).offset(offset).limit(limit)
    count_data = plants.count()

    return {
        "data": all_data.all(),
        "page_count": math.ceil(count_data / limit),
        "data_count": count_data,
        "current_page": page,
        "page_limit": limit,
    }

def create_plant(form_data: NewPlant, usr, db):

    unique_name = db.query(Plant).filter_by(name=form_data.name).first()
    if unique_name:
        raise HTTPException(status_code=400, detail="Bu nom band!") 

    new_plant = Plant(
        name=form_data.name,
        kpi=form_data.kpi
    )

    db.add(new_plant)
    db.flush()

    for p_u in form_data.plant_users:

        user = db.query(User).filter_by(id=p_u.user_id).filter(
            or_(User.role == "worker" , User.role == "plant_admin")
        ).first()
        
        if not user:
            raise HTTPException(status_code=400, detail="Hodim topilmadi!")

        shift = db.query(Shift).filter_by(id=p_u.shift_id).first()
        if not shift:
            raise HTTPException(status_code=400, detail="Smena topilmadi!")

        db.add(Plant_User(
            plant_id=new_plant.id,
            admin=p_u.admin,
            user_id=p_u.user_id,
            shift_id=p_u.shift_id,
            wage=p_u.wage,
            wage_period=p_u.wage_period,
        ))


    db.commit()

    raise HTTPException(status_code=200, detail="Ma`lumotlar saqlandi!")

def update_plant(id, form_data: UpdatePlant, usr, db: Session):
    plant = db.query(Plant).filter(Plant.id == id)
    this_plant = plant.first()
    
    if this_plant:
        unique_name = db.query(Plant).filter_by(name=form_data.name) \
                .filter(Plant.name != this_plant.name).first()
        
        if unique_name:
            raise HTTPException(status_code=400, detail="Bu nom band!") 

        plant.update({    
            Plant.name: form_data.name,
            Plant.kpi: form_data.kpi,
            Plant.disabled: form_data.disabled,
        })

        db.commit()

        raise HTTPException(status_code=200, detail="O`zgarish saqlandi!")
    else:
        raise HTTPException(status_code=400, detail="So`rovda xatolik!")
    
