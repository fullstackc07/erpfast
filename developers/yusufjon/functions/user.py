import math
from fastapi import HTTPException
from developers.yusufjon.models.phone import Phone
from developers.yusufjon.models.user import User
from developers.yusufjon.models.salary import Salary
from developers.yusufjon.models.workday import Workday
from developers.abdusamad.models import Markets
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func
import datetime
import calendar


def get_all_users(role, disabled: bool, search,  page, limit, usr, db: Session, market_id):
    if page == 1 or page < 1:
        offset = 0
    else:
        offset = (page-1) * limit

    users = db.query(User).filter_by(disabled=disabled).options(
        joinedload(User.phones).load_only(Phone.number),
    )

    if role:
        users = users.filter(User.role == role)

    # if type(balance).__name__ == 'float':
    #     if balance > 0:
    #         users = users.filter(User.balance > 0)

    if len(search) > 0:
        users = users.outerjoin(User.phones).filter(
            or_(
                User.name.like(f"%{search}%"),
                Phone.number.like(f"%{search}%"),
            )
        )
    if market_id:
        all_data = users.filter(User.market_id == market_id).order_by(
            User.id.desc()).offset(offset).limit(limit)
    else:
        all_data = users.order_by(User.id.desc()).offset(offset).limit(limit)
    count_data = users.count()

    all_user = []

    for one_users in all_data.all():
        one_users.market = db.query(Markets).filter_by(
            id=one_users.market_id).first()
        all_user.append(one_users)
    return {
        "data": all_user,
        "page_count": math.ceil(count_data / limit),
        "data_count": count_data,
        "current_page": page,
        "page_limit": limit,
    }


def calcWorkingDays(year, month, user):

    total_days = calendar.monthrange(year, month)[1]
    working_days = total_days

    for day in range(1, total_days+1):
        for holiday in user.holidays:
            if holiday.week_day == datetime.date(year, month, day).strftime('%A'):
                working_days -= 1

    return working_days


def calcDaily(year, month, user, salary):

    working_days = calcWorkingDays(year, month, user)
    if working_days > 0:
        return round(salary/working_days)
    else:
        return 0

def recalculate_salary(salary_id, user, db: Session):

    salary = db.query(Salary).filter_by(id=salary_id)
    salary_one = salary.first()
    if salary_one:
        if len(salary_one.allworkdays) > 0:
            workdays_sum = db.query(func.coalesce(func.sum(Workday.value), 0)).filter(Workday.salary_id==salary_one.id).scalar()
            daily =  calcDaily(salary_one.year, salary_one.month, user, salary_one.salary)
            salary.update({
                Salary.workdays: workdays_sum,
                Salary.daily: daily,
                Salary.calculated_wage: round(workdays_sum * daily)
            })
            db.commit()
        else:
            salary.delete()
            db.commit()
