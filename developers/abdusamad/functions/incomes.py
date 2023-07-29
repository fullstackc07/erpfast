from ..models import Incomes, Loans, Orders
from fastapi import HTTPException
from sqlalchemy import func, and_
from sqlalchemy.orm import joinedload
import math
from developers.yusufjon.models.user import User
from .loans import one_loan
from .orders import one_order
from .trades import one_trade


def all_incomes(from_time, to_time, order_id, loan_id, kassa_id, user_id, type, market_id, page, limit, db):
    if from_time and to_time :
        time_filter = func.date(Incomes.time).between(from_time, to_time)
    else :
        time_filter = Incomes.id > 0
    if order_id :
        order_filter = and_(Incomes.source == order_id, Incomes.type == "order")
    else :
        order_filter = Incomes.id > 0
    if loan_id :
        loan_filter = and_(Incomes.source == loan_id, Incomes.type == "loan")
    else :
        loan_filter = Incomes.id > 0
    if kassa_id :
        kassa_filter = and_(Incomes.kassa_id == kassa_id, Incomes.type == "user")
    else :
        kassa_filter = Incomes.id > 0
    if user_id :
        user_filter = and_(Incomes.source == user_id, Incomes.type == "user")
    else :
        user_filter = Incomes.id > 0
    if type :
        type_filter = Incomes.type == type
    else :
        type_filter = Incomes.id > 0
    incomes = db.query(Incomes).options(joinedload(Incomes.order), joinedload(Incomes.loan), joinedload(Incomes.user)).filter(time_filter, order_filter, loan_filter, kassa_filter, user_filter, type_filter, Incomes.market_id == market_id)
    return {"current_page": page, "limit": limit, "pages": math.ceil(incomes.count() / limit), "data": incomes.offset((page - 1) * limit).limit(limit).all()}


def sum_income(source, type, db):
    return db.query(func.coalesce(func.sum(Incomes.money), 0)).filter(Incomes.source == source, Incomes.type == type).scalar()


def take_money_from_loan(form, user, db):
    if one_loan(form.source, db) is None or one_loan(form.source, db).Loans.market_id != user.market_id or one_loan(form.source, db).Loans.status == True :
        raise HTTPException(status_code = 400, detail = "Bunday id raqamli faol nasiya mavjud emas")
    if one_loan(form.source, db).Loans.residual < form.money :
        raise HTTPException(status_code = 400, detail = "Olinayotgan summa nasiya summasidan katta bo'lmasligi kerak")
    elif one_loan(form.source, db).Loans.residual == form.money :
        db.query(Loans).filter(Loans.id == form.source).update({
            Loans.residual: 0,
            Loans.status: True
        })
    else :
        db.query(Loans).filter(Loans.id == form.source).update({
            Loans.residual: Loans.residual - form.money
        })
    new_income_db = Incomes(
        money = form.money,
        type = "loan",
        source = form.source,
        comment = form.comment,
        user_id = user.id,
        market_id = user.market_id,
    )
    db.query(User).filter(User.id == user.id).update({
        User.balance: User.balance + form.money
    })
    db.add(new_income_db)
    db.commit()
    db.refresh(new_income_db)
    return new_income_db


def take_money_from_order(form, user, db):
    if one_order(form.source, db) is None or one_order(form.source, db).market_id != user.market_id or one_order(form.source, db).status != "pre_order" :
        raise HTTPException(status_code = 400, detail = "Bunday id raqamli faol buyurtma mavjud emas")
    if float(one_trade(0, form.source, db)) - float(sum_income(form.source, "order", db)) < form.money :
        raise HTTPException(status_code = 400, detail = "Olinayotgan summa buyurtma summasidan katta bo'lmasligi kerak")
    new_income_db = Incomes(
        money = form.money,
        type = "order",
        source = form.source,
        comment = form.comment,
        user_id = user.id,
        market_id = user.market_id,
    )
    db.query(User).filter(User.id == user.id).update({
        User.balance: User.balance + form.money
    })
    db.add(new_income_db)
    db.commit()
    db.refresh(new_income_db)
    return new_income_db