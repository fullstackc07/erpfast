from fastapi import HTTPException
from ..models import Expenses, Kassa
import math
from sqlalchemy import func
from sqlalchemy.orm import joinedload, Session
from .fixed_expenses import *
from .kassa import one_kassa
from .orders import one_order
from developers.yusufjon.models.user import User
from developers.yusufjon.models.supplier import Supplier
from developers.yusufjon.models.salary import Salary
import datetime


def all_expenses(current_user, from_time, to_time, kassa_id, type, source, market_id, page, limit, db):
    if from_time and to_time:
        time_filter = func.date(Expenses.time).between(from_time, to_time)
    else:
        time_filter = Expenses.id > 0

    if kassa_id > 0:
        kassa_filter = Expenses.kassa_id == kassa_id
    else:
        kassa_filter = Expenses.id > 0

    if type:
        type_filter = Expenses.type == type
    else:
        type_filter = Expenses.id > 0

    if source:
        source_filter = Expenses.source == source
    else:
        source_filter = Expenses.id > 0

    if current_user.role in ['admin', 'accountant', 'analyst']:
        market_filter = Expenses.market_id > 0
    else:
        market_filter = Expenses.market_id == market_id

    expenses = db.query(Expenses).options(
        joinedload(Expenses.fixed_expense),
        joinedload(Expenses.kassa),
        joinedload(Expenses.user)
    ).filter(
        time_filter, kassa_filter,
        type_filter, source_filter, market_filter
    ).order_by(Expenses.id.desc())

    return {"current_page": page, "limit": limit, "pages": math.ceil(expenses.count() / limit), "data": expenses.offset((page - 1) * limit).limit(limit).all()}


def pay_money(form, user, db: Session):
    if form.type == "variable_expense":
        if one_kassa(form.kassa_id, db) is None or one_kassa(form.kassa_id, db).market_id != user.market_id:
            raise HTTPException(
                status_code=400, detail="Bunday kassa mavjud emas")
        if one_kassa(form.kassa_id, db).balance < form.money:
            raise HTTPException(
                statu=400, detail="Kassada yetarli mablag' mavjud emas")
        new_expense_db = Expenses(
            money=form.money,
            type=form.type,
            source=0,
            comment=form.comment,
            kassa_id=form.kassa_id,
            user_id=user.id,
            market_id=user.market_id,
        )
        db.add(new_expense_db)
        db.commit()
        db.refresh(new_expense_db)
        db.query(Kassa).filter(Kassa.id == form.kassa_id).update({
            Kassa.balance: Kassa.balance - form.money
        })
        db.commit()
    elif form.type == "fixed_expense":
        if one_kassa(form.kassa_id, db) is None or one_kassa(form.kassa_id, db).market_id != user.market_id:
            raise HTTPException(
                status_code=400, detail="Bunday kassa mavjud emas")
        if one_kassa(form.kassa_id, db).balance < form.money:
            raise HTTPException(
                status_code=400, detail="Kassada yetarli mablag' mavjud emas")
        if one_fixed_expense(form.source, db) is None:
            raise HTTPException(
                status_code=400, detail="Bunday chiqim turi mavjud emas")
        new_expense_db = Expenses(
            money=form.money,
            type=form.type,
            source=form.source,
            comment=form.comment,
            kassa_id=form.kassa_id,
            user_id=user.id,
            market_id=user.market_id,
        )
        db.add(new_expense_db)
        db.commit()
        db.refresh(new_expense_db)
        db.query(Kassa).filter(Kassa.id == form.kassa_id).update({
            Kassa.balance: Kassa.balance - form.money
        })
        db.commit()
    elif form.type == "order_expense":
        if one_order(form.source, db) is None or one_order(form.source, db).market_id != user.market_id or one_order(form.source, db).status != "pre_order":
            raise HTTPException(
                status_code=400, detail="Bunday buyurtma mavjud emas")
        if user.balance < form.money:
            raise HTTPException(
                status_code=400, detail="Hisobingizda yetarli mablag' mavjud emas")
        new_expense_db = Expenses(
            money=form.money,
            type=form.type,
            source=form.source,
            comment=form.comment,
            kassa_id=0,
            user_id=user.id,
            market_id=user.market_id,
        )
        db.add(new_expense_db)
        db.commit()
        db.refresh(new_expense_db)
        db.query(User).filter(User.id == user.id).update({
            User.balance: User.balance - form.money
        })
        db.commit()
    elif form.type == "user_expense":
        if one_kassa(form.kassa_id, db) is None or one_kassa(form.kassa_id, db).market_id != user.market_id:
            raise HTTPException(
                status_code=400, detail="Bunday kassa mavjud emas")
        user_verification = db.query(User).filter(
            User.id == form.source, User.disabled == False, User.market_id == user.market_id).first()
        if user_verification is None:
            raise HTTPException(
                status_code=400, detail="Bunday foydalanuvchi mavjud emas")
        if one_kassa(form.kassa_id, db).balance < form.money:
            raise HTTPException(
                status_code=400, detail="Kassada yetarli mablag' mavjud emas")
        new_expense_db = Expenses(
            money=form.money,
            type=form.type,
            source=form.source,
            comment=form.comment,
            kassa_id=form.kassa_id,
            user_id=user.id,
            market_id=user.market_id,
        )
        db.add(new_expense_db)
        db.commit()
        db.refresh(new_expense_db)
        db.query(Kassa).filter(Kassa.id == form.kassa_id).update({
            Kassa.balance: Kassa.balance - form.money
        })
        db.query(User).filter(User.id == user.id).update({
            User.balance: User.balance + form.money
        })
        db.commit()

    elif form.type == "supplier_payment":
        if one_kassa(form.kassa_id, db) is None:
            raise HTTPException(
                status_code=400, detail="Bunday kassa mavjud emas")

        supplier_verification = db.query(Supplier).filter(
            Supplier.id == form.source, Supplier.disabled == False).first()

        if supplier_verification is None:
            raise HTTPException(
                status_code=400, detail="Bunday foydalanuvchi mavjud emas")

        if one_kassa(form.kassa_id, db).balance < form.money:
            raise HTTPException(
                status_code=400, detail="Kassada yetarli mablag' mavjud emas")

        new_expense_db = Expenses(
            money=form.money,
            type=form.type,
            source=form.source,
            comment=form.comment,
            kassa_id=form.kassa_id,
            user_id=user.id,
            market_id=user.market_id,
        )

        db.add(new_expense_db)
        db.commit()
        db.refresh(new_expense_db)

        db.query(Kassa).filter(Kassa.id == form.kassa_id).update({
            Kassa.balance: Kassa.balance - form.money
        })

        db.query(Supplier).filter(Supplier.id == form.source).update({
            Supplier.balance: Supplier.balance - form.money
        })

        db.commit()

    elif form.type == "user_salary":
        if one_kassa(form.kassa_id, db) is None:
            raise HTTPException(
                status_code=400, detail="Bunday kassa mavjud emas")

        user_verification: User = db.query(User).filter(
            User.id == form.source, User.disabled == False).first()

        if user_verification is None:
            raise HTTPException(
                status_code=400, detail="Bunday foydalanuvchi mavjud emas")

        if one_kassa(form.kassa_id, db).balance < form.money:
            raise HTTPException(
                status_code=400, detail="Kassada yetarli mablag' mavjud emas")

        today = datetime.date.today()
        year = today.year
        month = today.month

        salary_date = datetime.date(year, month, user_verification.salaryDay)

        if datetime.date.today() < salary_date:
            y = (today.replace(day=1) - datetime.timedelta(days=1)).strftime("%Y")
            m = (today.replace(day=1) - datetime.timedelta(days=1)).strftime("%m")
        else:
            y = today.strftime("%Y")
            m = today.strftime("%m")

        salary = db.query(Salary).filter_by(
            year=y,
            month=m,
            user_id=user_verification.id
        ).first()

        if salary:
            new_expense_db = Expenses(
                money=form.money,
                type=form.type,
                source=form.source,
                comment=form.comment,
                kassa_id=form.kassa_id,
                user_id=user.id,
                market_id=user.market_id,
                salary_id=salary.id
            )

            db.add(new_expense_db)
            db.commit()
            db.refresh(new_expense_db)

            db.query(Kassa).filter(Kassa.id == form.kassa_id).update({
                Kassa.balance: Kassa.balance - form.money
            })

            db.commit()
            return new_expense_db
        else:
            raise HTTPException(status_code=400, detail="Oy uchun maosh yozilmagan!")
        
       

   
