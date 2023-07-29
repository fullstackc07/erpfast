import math
from sqlalchemy.orm import joinedload, Session
from fastapi import HTTPException
from developers.yusufjon.models.attandance import *
from developers.yusufjon.models.plant_user import *
from developers.yusufjon.models.salary import *
from developers.yusufjon.functions.user import *
from developers.yusufjon.models.workday import *
from developers.yusufjon.schemas.attandance import *
from developers.yusufjon.bot.bot import bot
from datetime import datetime
from sqlalchemy import func, or_
from developers.yusufjon.utils.trlatin import tarjima

WORKDAYS_IN_WEEK = 7
WORKDAYS_IN_MONTH = 31


def calculateWage(dateTime, last_davomat, user_id, plant_id, db: Session):
    plant_user = db.query(Plant_User).filter_by(
        plant_id=plant_id, user_id=user_id, disabled=False).first()
    if plant_user:

        from_time = datetime.strptime(
            plant_user.user.shift.from_time.strftime("%H:%M:%S"), "%H:%M:%S")
        to_time = datetime.strptime(
            plant_user.user.shift.to_time.strftime("%H:%M:%S"), "%H:%M:%S")

        daily_hours = round((to_time - from_time).total_seconds() / 3600, 2)

        if plant_user.wage_period == "daily":
            hourly_wage = round(plant_user.wage / daily_hours, 2)
        elif plant_user.wage_period == "weekly":
            hourly_wage = round(
                plant_user.wage / (daily_hours*WORKDAYS_IN_WEEK), 2)
        elif plant_user.wage_period == "monthly":
            hourly_wage = round(
                plant_user.wage / (daily_hours*WORKDAYS_IN_MONTH), 2)
        else:
            hourly_wage = plant_user.wage

        worked_from_time = datetime.strptime(
            last_davomat.datetime.strftime("%H:%M:%S"), "%H:%M:%S")
        try:

            worked_to_time = datetime.strptime(dateTime[-8:], "%H:%M:%S")

        except Exception as e:
            raise HTTPException(status_code=400, detail="")

        worked_hours = round(
            (worked_to_time - worked_from_time).total_seconds() / 3600, 2)
        wage = round(hourly_wage * worked_hours)

        if wage > 0:
            db.query(User).filter_by(id=user_id).update({
                User.salary: User.salary + wage
            })
            db.commit()

        return wage
    else:
        return 0


async def makeDavomat(user_id, plant_id, type, dateTime, authorizator_name, db: Session):

    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="Hodim topilmadi!")

    last_davomat = db.query(Attandance).filter(
        Attandance.user_id == user_id).order_by(Attandance.id.desc()).first()

    wage = error = 0

    dav_type = 'entry'
    if type == 'any':
        if last_davomat:
            if last_davomat.type == 'entry':
                dav_type = 'exit'
                wage = calculateWage(
                    dateTime, last_davomat, user_id, plant_id, db)

    elif type == 'entry':

        if last_davomat and last_davomat.type == 'entry':
            error += 1

    elif type == 'exit':

        if last_davomat:

            if last_davomat.type != 'entry':
                error += 1
            else:
                dav_type = 'exit'

                wage = calculateWage(
                    dateTime, last_davomat, user_id, plant_id, db)

        else:
            error += 1

    if error == 0:
        new_dav = Attandance(
            type=dav_type,
            user_id=user.id,
            wage=wage,
            plant_id=plant_id,
            authorizator=authorizator_name,
            datetime=dateTime,
        )

        db.add(new_dav)

        check_salary = db.query(Salary).filter_by(
            year=int(dateTime[0:4]),
            month=int(dateTime[5:7]),
            user_id=user.id
        ).first()

        if not check_salary:
            check_salary = Salary(
                user_id=user.id,
                year=int(dateTime[0:4]),
                month=int(dateTime[5:7]),
                salary=user.salary or 0,
            )
            db.add(check_salary)
            db.flush()

        check_workday = db.query(Workday).filter_by(
            user_id=user.id,
            salary_id=check_salary.id,
            date=dateTime[:10]
        ).first()

        if not check_workday:
            check_workday = Workday(
                salary_id=check_salary.id,
                date=dateTime[:10],
                value=1,
                user_id=user.id
            )
            db.add(check_workday)
    

        db.commit()

        recalculate_salary(check_salary.id, user, db)

        for bot_chat in user.bot_chats:
            if bot_chat.login == True:
                vaqt_min = datetime.fromisoformat(dateTime).strftime("%H:%M")
                if new_dav.type == 'entry':
                    text = f'🟢 Kirgan vaqt:{vaqt_min} ({authorizator_name})'
                else:
                    text = f'🔴 Chiqqan vaqt: {vaqt_min} Hisoblandi:  {new_dav.wage} tenge {authorizator_name}'

                await bot.send_message(chat_id=bot_chat.chat_id, text=text)


def get_all_attandances(_date, search, plant_id, user_id, page, limit, usr, db: Session):
    if page == 1 or page < 1:
        offset = 0
    else:
        offset = (page-1) * limit

    attandances = db.query(Attandance).options(
        joinedload(Attandance.plant).load_only(Plant.name),
        joinedload(Attandance.user).load_only(User.name),
        joinedload(Attandance.building).load_only(Building.name),
    )

    if plant_id > 0:
        attandances = attandances.filter(Attandance.plant_id == plant_id)

    if user_id > 0:
        attandances = attandances.filter(Attandance.user_id == user_id)
    
    if len(_date) > 0:
        attandances = attandances.filter(func.date(Attandance.datetime) == _date)

    if len(search) > 0:

        attandances = attandances.join(Attandance.user).filter(
            or_(
                User.name.like(f"%{tarjima(search, 'ru')}%"),
                User.name.like(f"%{tarjima(search, 'uz')}%"),
                Attandance.authorizator.like(f"%{tarjima(search, 'ru')}%"),
                Attandance.authorizator.like(f"%{tarjima(search, 'uz')}%"),
            )

        )

    all_data = attandances.order_by(
        Attandance.id.desc()).offset(offset).limit(limit)
    count_data = attandances.count()

    return {
        "data": all_data.all(),
        "page_count": math.ceil(count_data / limit),
        "data_count": count_data,
        "current_page": page,
        "page_limit": limit,
    }


def create_attandance(type: AttType, form_data: NewAttandance, usr, db: Session):

    new_attandance = Attandance(
        type=form_data.type,
        user_id=form_data.user_id,
        wage=form_data.wage,
        authorizator=form_data.authorizator,
        datetime=form_data.datetime,
    )

    db.add(new_attandance)
    db.commit()

    raise HTTPException(status_code=200, detail="Ma`lumotlar saqlandi!")


def update_attandance(id, form_data: UpdateAttandance, usr, db: Session):
    attandance = db.query(Attandance).filter(Attandance.id == id)
    this_attandance = attandance.first()
    if this_attandance:
        attandance.update({
            Attandance.type: form_data.type,
            Attandance.user_id: form_data.user_id,
            Attandance.wage: form_data.wage,
            Attandance.authorizator: form_data.authorizator,
            Attandance.datetime: form_data.datetime,
        })
        db.commit()

        raise HTTPException(status_code=200, detail="O`zgarish saqlandi!")
    else:
        raise HTTPException(status_code=400, detail="So`rovda xatolik!")
