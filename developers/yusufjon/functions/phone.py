from developers.yusufjon.utils.main import *
from developers.yusufjon.models.phone import *

def get_all_phones(search, page, limit, usr, db):
    if page == 1 or page < 1:
        offset = 0
    else:
        offset = (page-1) * limit
    
    phones = db.query(Phone)
    phones = looking_for(search, phones)
    all_data = phones.order_by(Phone.id.desc()).offset(offset).limit(limit)
    count_data = phones.count()

    return {
        "data": all_data.all(),
        "page_count": math.ceil(count_data / limit),
        "data_count": count_data,
        "current_page": page,
        "page_limit": limit,
    }

def create_phone(form_data, usr, db):
    new_phone = Phone(
        number=form_data.number,
        owner_id=form_data.owner_id,
        ownerType=form_data.ownertype,
    )

    db.add(new_phone)
    db.commit()

    raise HTTPException(status_code=200, detail="Ma`lumotlar saqlandi!")

def update_phone(id, form_data, usr, db):
    phone = db.query(Phone).filter(Phone.id == id)
    this_phone = phone.first()
    if this_phone:
        phone.update({    
            Phone.number: form_data.number,
            Phone.owner_id: form_data.owner_id,
            Phone.ownerType: form_data.ownertype,
        })
        db.commit()

        raise HTTPException(status_code=200, detail="O`zgarish saqlandi!")
    else:
        raise HTTPException(status_code=400, detail="So`rovda xatolik!")
    
