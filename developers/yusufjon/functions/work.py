import math
from sqlalchemy.orm import joinedload, Session
from fastapi import HTTPException
from developers.yusufjon.models.work import *
from developers.yusufjon.schemas.work import *

def get_all_works(cycle_id, page, limit, usr, db: Session):
    if page == 1 or page < 1:
        offset = 0
    else:
        offset = (page-1) * limit
    
    works = db.query(Work).filter_by(cycle_id=cycle_id, disabled=False)
    all_data = works.order_by(Work.id.desc()).offset(offset).limit(limit)
    count_data = works.count()

    return {
        "data": all_data.all(),
        "page_count": math.ceil(count_data / limit),
        "data_count": count_data,
        "current_page": page,
        "page_limit": limit,
    }

def create_work(form_datas, usr, db: Session):

    for form_data in form_datas:
        new_work = Work(
            cycle_id=form_data.cycle_id,
            name=form_data.name,
        )

        db.add(new_work)
    db.commit()

    raise HTTPException(status_code=200, detail="Ma`lumotlar saqlandi!")

def update_work(id, form_data: UpdateWork, usr, db: Session):
    work = db.query(Work).filter(Work.id == id)
    this_work = work.first()
    if this_work:
        work.update({    
            Work.cycle_id: form_data.cycle_id,
            Work.name: form_data.name,
            Work.disabled: form_data.disabled,
        })
        db.commit()

        raise HTTPException(status_code=200, detail="O`zgarish saqlandi!")
    else:
        raise HTTPException(status_code=400, detail="So`rovda xatolik!")
    
