from fastapi import HTTPException
from ..models import Markets
import math
from developers.yusufjon.models.phone import Phone
from sqlalchemy.orm import joinedload


def all_markets(search, page, limit, db):
    if search :
        search_formatted = "%{}%".format(search)
        search_filter = (Markets.name.like(search_formatted) | (Markets.address == search) | (Phone.number.like(search_formatted)))
    else :
        search_filter = Markets.id > 0
    markets = db.query(Markets).join(Markets.phones).options(joinedload(Markets.user)).filter(search_filter).order_by(Markets.name.asc())
    return {"current_page": page, "limit": limit, "pages": math.ceil(markets.count() / limit), "data": markets.offset((page - 1) * limit).limit(limit).all()}


def one_market(id, db):
    return db.query(Markets).options(joinedload(Markets.user)).filter(Markets.id == id).first()


def create_market(form, user, db):
    # phones_verification = db.query(Phone).filter(Phone.number.in_([phone.phone for phone in form.phones]), Phone.).first()
    # if phones_verification :
    #     raise HTTPException(status_code = 400, detail = "Bunday telefon raqam mavjud")
    new_market_db = Markets(
        name = form.name,
        address = form.address,
        user_id = user.id
    )
    db.add(new_market_db)
    db.commit()
    db.refresh(new_market_db)
    for phone in form.phones :
        new_phone_db = Phone(
            number = phone.phone,
            owner_id = new_market_db.id,
            ownerType = "market"
        )
        db.add(new_phone_db)
        db.commit()
        db.refresh(new_phone_db)
    return new_market_db


def update_market(form, user, db):
    if one_market(form.id, db) is None :
        raise HTTPException(status_code = 400, detail = "Bunday id raqamli magazin mavjud emas")
    db.query(Markets).filter(Markets.id == form.id).update({
        Markets.name: form.name,
        Markets.address: form.address,
        Markets.user_id: user.id
    })
    db.commit()
    db.query(Phone).filter(Phone.owner_id == form.id, Phone.ownerType == "market").delete()
    db.commit()
    for phone in form.phones :
        new_phone_db = Phone(
            number = phone.phone,
            owner_id = form.id,
            ownerType = "market"
        )
        db.add(new_phone_db)
        db.commit()
        db.refresh(new_phone_db)