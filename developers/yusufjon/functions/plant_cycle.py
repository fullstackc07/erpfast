import math
from sqlalchemy.orm import joinedload, Session
from fastapi import HTTPException
from developers.yusufjon.models.plant_cycle import *

def get_all_plant_cycles(plant_id, cycle_id, search, disabled, page, limit, usr, db):
    if page == 1 or page < 1:
        offset = 0
    else:
        offset = (page-1) * limit
    
    plant_cycles = db.query(Plant_Cycle).options(
        joinedload(Plant_Cycle.plant),
        joinedload(Plant_Cycle.cycle).subqueryload(Cycle.product_type)
    ).filter(Plant_Cycle.disabled == disabled)

    if plant_id > 0:
        plant_cycles = plant_cycles.filter(Plant_Cycle.plant_id == plant_id)

    if cycle_id > 0:
        plant_cycles = plant_cycles.filter(Plant_Cycle.cycle_id == cycle_id)
    

    #if search:
       #plant_cycles = plant_cycles.filter(
           #Plant_Cycle.id.like(f"%{search}%"),
       #)

    all_data = plant_cycles.order_by(Plant_Cycle.id.desc()).offset(offset).limit(limit)
    count_data = plant_cycles.count()

    return {
        "data": all_data.all(),
        "page_count": math.ceil(count_data / limit),
        "data_count": count_data,
        "current_page": page,
        "page_limit": limit,
    }

def create_plant_cycle(form_data, usr, db):
    new_plant_cycle = Plant_Cycle(
        cycle_id=form_data.cycle_id,
        plant_id=form_data.plant_id,
        disabled=form_data.disabled,
        hidden=form_data.hidden,
    )

    db.add(new_plant_cycle)
    db.commit()

    raise HTTPException(status_code=200, detail="Ma`lumotlar saqlandi!")

def update_plant_cycle(id, form_data, usr, db):
    plant_cycle = db.query(Plant_Cycle).filter(Plant_Cycle.id == id)
    this_plant_cycle = plant_cycle.first()
    if this_plant_cycle:
        plant_cycle.update({    
            Plant_Cycle.cycle_id: form_data.cycle_id,
            Plant_Cycle.plant_id: form_data.plant_id,
            Plant_Cycle.disabled: form_data.disabled,
            Plant_Cycle.hidden: form_data.hidden,
        })
        db.commit()

        raise HTTPException(status_code=200, detail="O`zgarish saqlandi!")
    else:
        raise HTTPException(status_code=400, detail="So`rovda xatolik!")
    
