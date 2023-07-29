import math
from sqlalchemy.orm import joinedload, Session
from fastapi import HTTPException
from developers.yusufjon.models.olchov_proportion import *

def get_all_olchov_proportions(abs_olchov_id, page, limit, usr, db: Session):
    if page == 1 or page < 1:
        offset = 0
    else:
        offset = (page-1) * limit
    
    olchov_proportions = db.query(
        Olchov_Proportion.id.label("olchov_proportion_id"),
        Olchov_Proportion.value,
        Olchov.name.label("olchov_name"),
        Olchov.id.label("olchov_id"),
    ).filter(
        Olchov_Proportion.abs_olchov_id==abs_olchov_id
    ).join(Olchov_Proportion.rel_olchov)

    all_data = olchov_proportions.order_by(Olchov_Proportion.id.desc()).offset(offset).limit(limit)
    count_data = olchov_proportions.count()

    return {
        "data": all_data.all(),
        "page_count": math.ceil(count_data / limit),
        "data_count": count_data,
        "current_page": page,
        "page_limit": limit,
    }

def create_olchov_proportion(form_data, usr, db):
    new_olchov_proportion = Olchov_Proportion(
        abs_olchov_id=form_data.abs_olchov_id,
        rel_olchov_id=form_data.rel_olchov_id,
        value=form_data.value,
    )

    db.add(new_olchov_proportion)
    db.commit()

    raise HTTPException(status_code=200, detail="Ma`lumotlar saqlandi!")

def update_olchov_proportion(id, form_data, usr, db):
    olchov_proportion = db.query(Olchov_Proportion).filter(Olchov_Proportion.id == id)
    this_olchov_proportion = olchov_proportion.first()
    if this_olchov_proportion:
        olchov_proportion.update({    
            Olchov_Proportion.abs_olchov_id: form_data.abs_olchov_id,
            Olchov_Proportion.rel_olchov_id: form_data.rel_olchov_id,
            Olchov_Proportion.value: form_data.value,
        })
        db.commit()

        raise HTTPException(status_code=200, detail="O`zgarish saqlandi!")
    else:
        raise HTTPException(status_code=400, detail="So`rovda xatolik!")
    
