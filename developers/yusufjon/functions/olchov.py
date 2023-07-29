import math
from sqlalchemy.orm import joinedload, Session
from fastapi import HTTPException
from developers.yusufjon.models.olchov import *

def get_all_olchovs(search, page, limit, usr, db):
    if page == 1 or page < 1:
        offset = 0
    else:
        offset = (page-1) * limit
    
    olchovs = db.query(Olchov)

    if search:
       olchovs = olchovs.filter(
           Olchov.name.like(f"%{search}%"),
       )

    all_data = olchovs.order_by(Olchov.id.desc()).offset(offset).limit(limit)
    count_data = olchovs.count()

    return {
        "data": all_data.all(),
        "page_count": math.ceil(count_data / limit),
        "data_count": count_data,
        "current_page": page,
        "page_limit": limit,
    }

def create_olchov(form_data, usr, db):
    new_olchov = Olchov(
        name=form_data.name,
    )

    db.add(new_olchov)
    db.commit()

    raise HTTPException(status_code=200, detail="Ma`lumotlar saqlandi!")

def update_olchov(id, form_data, usr, db):
    olchov = db.query(Olchov).filter(Olchov.id == id)
    this_olchov = olchov.first()
    if this_olchov:
        olchov.update({    
            Olchov.name: form_data.name,
        })
        db.commit()

        raise HTTPException(status_code=200, detail="O`zgarish saqlandi!")
    else:
        raise HTTPException(status_code=400, detail="So`rovda xatolik!")
    
