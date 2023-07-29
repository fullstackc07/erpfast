from fastapi import HTTPException
from ..models import Fixed_expenses
import math
from sqlalchemy.orm import joinedload


def all_fixed_expenses(search, market_id, page, limit, db):
    if search :
        search_formatted = "%{}%".format(search)
        search_filter = Fixed_expenses.name.like(search_formatted)
    else :
        search_filter = Fixed_expenses.id > 0
    fixed_expenses = db.query(Fixed_expenses).options(joinedload(Fixed_expenses.user)).filter(search_filter, Fixed_expenses.market_id == market_id).order_by(Fixed_expenses.name.asc())
    return {"current_page": page, "limit": limit, "pages": math.ceil(fixed_expenses.count() / limit), "data": fixed_expenses.offset((page - 1) * limit).limit(limit).all()}


def one_fixed_expense(id, db):
    return db.query(Fixed_expenses).options(joinedload(Fixed_expenses.user)).filter(Fixed_expenses.id == id).first()


def create_fixed_expense(form, user, db):
    fixed_expenses_verification = db.query(Fixed_expenses).filter(Fixed_expenses.name == form.name, Fixed_expenses.market_id == user.market_id).first()
    if fixed_expenses_verification :
        raise HTTPException(status_code = 400, detail = "Bunday chiqim turi mavjud")
    new_fixed_expense_db = Fixed_expenses(
        name = form.name,
        user_id = user.id,
        market_id = user.market_id
    )
    db.add(new_fixed_expense_db)
    db.commit()
    db.refresh(new_fixed_expense_db)
    return new_fixed_expense_db


def update_fixed_expense(form, user, db) :
    if one_fixed_expense(form.id, db) is None or one_fixed_expense(form.id, db).market_id != user.market_id :
        raise HTTPException(status_code = 400, detail = "Bunday chiqim turi mavjud emas")
    fixed_expenses_verification = db.query(Fixed_expenses).filter(Fixed_expenses.name == form.name, Fixed_expenses.market_id == user.market_id).first()
    if fixed_expenses_verification and fixed_expenses_verification.id != one_fixed_expense(form.id, db).id :
        raise HTTPException(status_code = 400, detail = "Bunday chiqim turi mavjud")
    db.query(Fixed_expenses).filter(Fixed_expenses.id == form.id).update({
        Fixed_expenses.name: form.name,
        Fixed_expenses.user_id: user.id
    })
    db.commit()