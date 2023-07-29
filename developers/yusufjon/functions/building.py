import math
from sqlalchemy.orm import joinedload, Session
from fastapi import HTTPException
from developers.yusufjon.models.building import *
from developers.yusufjon.schemas.building import *
from developers.yusufjon.utils.trlatin import tarjima
from sqlalchemy.sql import or_

def get_all_buildings(disabled, search, page, limit, usr, db: Session):
    if page == 1 or page < 1:
        offset = 0
    else:
        offset = (page-1) * limit
    
    buildings = db.query(Building).filter(Building.disabled == disabled)

    if search:
        buildings = buildings.filter(
            or_(
                Building.name.like(f"%{tarjima(search, 'ru')}%"),
                Building.name.like(f"%{tarjima(search, 'uz')}%"),
            )
        )
    
    all_data = buildings.order_by(Building.id.desc()).offset(offset).limit(limit)
    count_data = buildings.count()

    return {
        "data": all_data.all(),
        "page_count": math.ceil(count_data / limit),
        "data_count": count_data,
        "current_page": page,
        "page_limit": limit,
    }

def create_building(form_data: NewBuilding, usr, db: Session):

    unique_user = db.query(Building).filter_by(name=form_data.name).first()

    if unique_user:
        raise HTTPException(status_code=400, detail="Bu nom band!")
    
    new_building = Building(
        name=form_data.name
    )

    db.add(new_building)
    db.commit()

    raise HTTPException(status_code=200, detail="Ma`lumotlar saqlandi!")

def update_building(id, form_data: UpdateBuilding, usr, db: Session):
    building = db.query(Building).filter(Building.id == id)
    this_building = building.first()
    if this_building:

        unique_user = db.query(Building).filter_by(name=form_data.name).filter(Building.name != this_building.name).first()

        if unique_user:
            raise HTTPException(status_code=400, detail="Bu nom band!")

        building.update({    
            Building.name: form_data.name,
            Building.disabled: form_data.disabled,
        })
        db.commit()

        raise HTTPException(status_code=200, detail="O`zgarish saqlandi!")
    else:
        raise HTTPException(status_code=400, detail="So`rovda xatolik!")
    
