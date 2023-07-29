from fastapi import HTTPException
from developers.abdusamad.models import Expenses, Kassa
import math
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from developers.yusufjon.models.user import User


def get_expenses(from_time, to_time, kassa_id, type, source, market_id, page, limit, db, usr):

    if page == 1 or page < 1:
        offset = 0
    else:
        offset = (page-1) * limit
    if from_time and to_time :
        time_filter = func.date(Expenses.time).between(from_time, to_time)
    else : 
        time_filter = Expenses.id > 0
    if kassa_id :
        kassa_filter = Expenses.kassa_id == kassa_id
    else :
        kassa_filter = Expenses.id > 0
    if type :
        type_filter = Expenses.type == type
    else :
        type_filter = Expenses.id > 0
    if market_id :
        market_filter = Expenses.market_id == market_id
    else :
        market_filter = Expenses.id > 0
    if source :
        source_filter = Expenses.source == source
    else :
        source_filter = Expenses.id > 0

    expenses = db.query(Expenses).options(joinedload(Expenses.user))\
    .filter(time_filter, kassa_filter, type_filter, market_filter,source_filter)

    all_data = expenses.order_by(Expenses.id.asc()).offset(offset).limit(limit)

    count_data = expenses.count()

    return {
        "data": all_data.all(),
        "page_count":  math.ceil(expenses.count() / limit),
        "data_count": count_data,
        "current_page": page,
        "page_limit": limit,
    }



def test_get_expenses(from_time, to_time, kassa_id, type, source, market_id, page, limit, db, usr):

    if page == 1 or page < 1:
        offset = 0
    else:
        offset = (page-1) * limit
    if from_time and to_time :
        time_filter = func.date(Expenses.time).between(from_time, to_time)
    else : 
        time_filter = Expenses.id > 0
    if kassa_id :
        kassa_filter = Expenses.kassa_id == kassa_id
    else :
        kassa_filter = Expenses.id > 0
    if type :
        type_filter = Expenses.type == type
    else :
        type_filter = Expenses.id > 0
    if market_id :
        market_filter = Expenses.market_id == market_id
    else :
        market_filter = Expenses.id > 0
    if source :
        source_filter = source == User.id
    else :
        source_filter = Expenses.id > 0
        
    expenses = db.query(Expenses, User)\
    .join(Expenses.user)\
    .filter(time_filter,kassa_filter,type_filter,market_filter,source_filter)

    all_data = expenses.order_by(Expenses.id.asc()).offset(offset).limit(limit)

    count_data = expenses.count()

    return {
        "data": all_data.all(),
        "page_count":  math.ceil(expenses.count() / limit),
        "data_count": count_data,
        "current_page": page,
        "page_limit": limit,
    }
