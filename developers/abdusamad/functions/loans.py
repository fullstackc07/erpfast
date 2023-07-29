from ..models import Loans, Orders, Incomes
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import label
import math


def all_loans(from_time, to_time, customer_id, status, market_id, page, limit, db):
    if from_time and to_time :
        time_filter = func.date(Orders.time).between(from_time, to_time)
    else :
        time_filter = Loans.id > 0
    if customer_id :
        customer_filter = Orders.customer_id
    else :
        customer_filter = Loans.id > 0
    if status in [True, False] :
        status_filter = Loans.status == status
    else :
        status_filter = Loans.id > 0
    sum_income = db.query(func.coalesce(func.sum(Incomes.money), 0)).filter(Incomes.source == Loans.id, Incomes.type == "loan", Incomes.market_id == market_id).subquery()
    loans = db.query(Loans, label("sum_income", sum_income)).options(joinedload(Loans.order).subqueryload(Orders.customer)).filter(time_filter, customer_filter, status_filter, Loans.market_id == market_id)
    return {"current_page": page, "limit": limit, "pages": math.ceil(loans.count() / limit), "data": loans.offset((page - 1) * limit).limit(limit).all()}


def one_loan(id, db):
    sum_income = db.query(func.coalesce(func.sum(Incomes.money), 0)).filter(Incomes.source == Loans.id, Incomes.type == "loan").subquery()
    return db.query(Loans, label("sum_income", sum_income)).options(joinedload(Loans.order).subqueryload(Orders.customer)).filter(Loans.id == id).first()