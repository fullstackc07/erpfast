from fastapi import HTTPException
from ..models import Customers
import math
from developers.yusufjon.models.phone import Phone
from sqlalchemy.orm import joinedload
from .markets import one_market


def all_customers(search, market_id, page, limit, db):
    if search :
        search_formatted = "%{}%".format(search)
        search_filter = (Customers.name.like(search_formatted) | (Customers.type == search) | (Phone.number.like(search_formatted)))
    else :
        search_filter = Customers.id > 0
    customers = db.query(Customers).join(Customers.phones).options(joinedload(Customers.user)).filter(search_filter, Customers.market_id == market_id).order_by(Customers.name.asc())
    return {"current_page": page, "limit": limit, "pages": math.ceil(customers.count() / limit), "data": customers.offset((page - 1) * limit).limit(limit).all()}


def one_customer(id, db):
    return db.query(Customers).options(joinedload(Customers.user)).filter(Customers.id == id).first()


def create_customer(form, user, db):
    # phones_verification = db.query(Phone).filter(Phone.number.in_([phone.phone for phone in form.phones])).first()
    # if phones_verification :
    #     raise HTTPException(status_code = 400, detail = "Bunday telefon raqam mavjud")
    if one_market(user.market_id, db) is None :
        raise HTTPException(status_code = 400, detail = "Bunday magazin mavjud emas")
    new_customer_db = Customers(
        name = form.name,
        type = form.type,
        user_id = user.id,
        market_id = user.market_id
    )
    db.add(new_customer_db)
    db.commit()

    for phone in form.phones :
        new_phone_db = Phone(
            number = phone.phone,
            owner_id = new_customer_db.id,
            ownerType = "customer"
        )
        db.add(new_phone_db)
        db.commit()

    return db.query(Customers.id, Customers.name).filter_by(id=new_customer_db.id).first()


def update_customer(form, user, db):
    if one_customer(form.id, db) is None or one_customer(form.id, db).market_id != user.market_id :
        raise HTTPException(status_code = 400, detail = "Bunday id raqamli mijoz mavjud emas")
    db.query(Customers).filter(Customers.id == form.id).update({
        Customers.name: form.name,
        Customers.type: form.type,
        Customers.user_id: user.id
    })
    db.commit()
    db.query(Phone).filter(Phone.owner_id == form.id, Phone.ownerType == "customer").delete()
    db.commit()
    for phone in form.phones :
        new_phone_db = Phone(
            number = phone.phone,
            owner_id = form.id,
            ownerType = "customer"
        )
        db.add(new_phone_db)
        db.commit()
        db.refresh(new_phone_db)