import math
from sqlalchemy.orm import joinedload, Session
from fastapi import HTTPException
from developers.yusufjon.models.shift import *

def get_all_shifts(page, limit, usr, db):
    if page == 1 or page < 1:
        offset = 0
    else:
        offset = (page-1) * limit
    
    shifts = db.query(Shift)

    all_data = shifts.order_by(Shift.id.desc()).offset(offset).limit(limit)
    count_data = shifts.count()

    return {
        "data": all_data.all(),
        "page_count": math.ceil(count_data / limit),
        "data_count": count_data,
        "current_page": page,
        "page_limit": limit,
    }

def create_shift(form_data, usr, db):
    new_shift = Shift(
        from_time=form_data.from_time,
        name=form_data.name,
        to_time=form_data.to_time,
    )

    db.add(new_shift)
    db.commit()

    raise HTTPException(status_code=200, detail="Ma`lumotlar saqlandi!")

def update_shift(id, form_data, usr, db):
    shift = db.query(Shift).filter(Shift.id == id)
    this_shift = shift.first()
    if this_shift:
        shift.update({    
            Shift.name: form_data.name,
            Shift.from_time: form_data.from_time,
            Shift.to_time: form_data.to_time,
        })
        db.commit()

        raise HTTPException(status_code=200, detail="O`zgarish saqlandi!")
    else:
        raise HTTPException(status_code=400, detail="So`rovda xatolik!")
    
