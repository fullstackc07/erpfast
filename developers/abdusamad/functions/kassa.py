from fastapi import HTTPException
from ..models import Kassa, Incomes
from developers.yusufjon.models.user import User


def all_kassa(search, market_id, db):
    if search :
        search_formatted = "%{}%".format(search)
        search_filter = (Kassa.name.like(search_formatted)) | (Kassa.comment.like(search_formatted))
    else :
        search_filter = Kassa.id > 0
    return db.query(Kassa).filter(search_filter, Kassa.market_id == market_id).order_by(Kassa.name.asc()).all()


def one_kassa(id, db):
    return db.query(Kassa).filter(Kassa.id == id).first()


def create_kassa(form, user, db):
    kassa_verification = db.query(Kassa).filter(Kassa.name == form.name, Kassa.market_id == user.market_id).first()
    if kassa_verification :
        raise HTTPException(status_code = 400, detail = "Bunday kassa mavjud")
    new_kassa_db = Kassa(
        name = form.name,
        comment = form.comment,
        user_id = user.id,
        market_id = user.market_id
    )
    db.add(new_kassa_db)
    db.commit()
    db.refresh(new_kassa_db)
    return new_kassa_db


def update_kassa(form, user, db) :
    if one_kassa(form.id, db) is None or one_kassa(form.id, db).market_id != user.market_id :
        raise HTTPException(status_code = 400, detail = "Bunday kassa mavjud emas")
    kassa_verification = db.query(Kassa).filter(Kassa.name == form.name, Kassa.market_id == user.market_id).first()
    if kassa_verification and kassa_verification.id != form.id :
        raise HTTPException(status_code = 400, detail = "Bunday kassa mavjud")
    db.query(Kassa).filter(Kassa.id == form.id).update({
        Kassa.name: form.name,
        Kassa.comment: form.comment,
        Kassa.user_id: user.id
    })
    db.commit()


def take_money_from_user(form, user, db) :
    if one_kassa(form.kassa_id, db) is None or one_kassa(form.kassa_id, db).market_id != user.market_id :
        raise HTTPException(status_code = 400, detail = "Bunday kassa mavjud emas")
    user_ver = db.query(User).filter(User.id == form.user_id, User.market_id == user.market_id).first()
    if user_ver is None or user_ver.balance < form.money :
        raise HTTPException(status_code = 400, detail = "Ushbu hodim balansida yetarli mablag' mavjud emas")
    new_income_db = Incomes(
        money = form.money,
        type = "user",
        source = form.user_id,
        comment = form.comment,
        user_id = user.id,
        kassa_id = form.kassa_id,
        market_id = user.market_id
    )
    db.query(Kassa).filter(Kassa.id == form.kassa_id).update({
        Kassa.balance: Kassa.balance + form.money
    })
    db.query(User).filter(User.id == form.user_id).update({
        User.balance: User.balance - form.money
    })
    db.add(new_income_db)
    db.commit()
    db.refresh(new_income_db)