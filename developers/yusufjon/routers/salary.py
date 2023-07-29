from fastapi import HTTPException, APIRouter, Depends, Body
from typing import Optional
from developers.yusufjon.schemas.user import NewUser
from security.auth import get_current_active_user
from databases.main import ActiveSession
from sqlalchemy.orm import joinedload, Session
from sqlalchemy.sql import label
from developers.yusufjon.models.salary import *
from developers.yusufjon.models.workday import *
from developers.yusufjon.models.user import *
from developers.yusufjon.functions.user import *
from developers.abdusamad.models import Expenses
import math
import calendar
from pydantic import Field, BaseModel

salary_router = APIRouter(tags=['Salary Endpoint'])

@salary_router.get("/salaries", description="This router returns list of the salaries using pagination")
async def get_salaries_list(
    year: int,
    month: int,
    page: int = 1,
    limit: int = 10,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):   
    if usr.role in ['admin', 'accountant', 'analyst']:
        if page == 1 or page < 1:
            offset = 0
        else:
            offset = (page-1) * limit

        avanse = db.query(func.coalesce(func.sum(Expenses.money), 0)).filter(
            Expenses.type=='user_salary',
            Expenses.source==User.id,
            Expenses.salary_id==Salary.id
        ).subquery()

        salaries = db.query(Salary, User.name, label('avanse', avanse)).options(
            joinedload(Salary.allworkdays).subqueryload(Workday.attandances),
        ).join(Salary.user).filter(
            Salary.year==year,
            Salary.month==month,
        )

        all_data = salaries.order_by(User.name.asc()).offset(offset).limit(limit)
        count_data = salaries.count()

        return {
            "data": all_data.all(),
            "page_count": math.ceil(count_data / limit),
            "data_count": count_data,
            "current_page": page,
            "page_limit": limit,
            "days_count": calendar.monthrange(year, month)[1],
        }
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")  

@salary_router.put("/workday/{id}/update", description="This router is able to update shift")
async def update_one_workday(
    id: int,
    value: float=Body(1, ge=0.1),
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst']:

        workday = db.query(Workday).filter_by(id=id)
        this_workday = workday.first()

        if this_workday:
            workday.update({Workday.value: value})
            db.commit()
            recalculate_salary(this_workday.salary_id, this_workday.user, db)
            return "success"
        else:
            raise HTTPException(status_code=400, detail="Ish kuni topilmadi!")


    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")


class SalarySchema(BaseModel):
    calculated_wage: float = Field(..., ge=0)
    additional_wage: float = Field(..., ge=0)
    tax: float = Field(..., ge=0)
    

@salary_router.put("/salary/{id}/update", description="This router is able to update shift")
async def update_one_salary(
    id: int,
    form_data: SalarySchema,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst']:

        salary = db.query(Salary).filter_by(id=id)
        this_salary = salary.first()

        if this_salary:
            salary.update({
                Salary.additional_wage: form_data.additional_wage,
                Salary.tax: form_data.tax,
                Salary.calculated_wage: form_data.calculated_wage,
            })
            db.commit()
            return "success"
        else:
            raise HTTPException(status_code=400, detail="Ish kuni topilmadi!")


    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")
    


@salary_router.put("/salary_value/{id}/update", description="This router is able to update shift")
async def update_one_salary(
    id: int,
    salary: float = Body(..., ge=0),
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst']:

        _salary = db.query(Salary).filter_by(id=id)
        this_salary = _salary.first()

        if this_salary:

            _salary.update({
                Salary.salary: salary,
            })
            db.commit()
            recalculate_salary(this_salary.id, this_salary.user, db)
            return "success"
        else:
            raise HTTPException(status_code=400, detail="Ish kuni topilmadi!")


    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")