from fastapi import HTTPException, APIRouter, Depends, Request
from typing import Optional, List
from developers.yusufjon.schemas.user import NewUser
from security.auth import get_current_active_user
from databases.main import ActiveSession
from sqlalchemy.orm import joinedload, Session
from developers.yusufjon.models.attandance import *
from developers.yusufjon.functions.attandance import *
from developers.yusufjon.schemas.attandance import *
import json
import uuid
from datetime import datetime, date

attandance_router = APIRouter(tags=['Attandance Endpoint'])

@attandance_router.get("/attandances")
async def get_attandances(
    search: Optional[str] = "",
    plant_id: Optional[int] = 0,
    _date: Optional[date] = "",
    user_id: Optional[int] = 0,
    page: Optional[int] = 1,
    limit: Optional[int] = 10,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst']:
        return get_all_attandances(_date, search, plant_id, user_id, page, limit, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")  

@attandance_router.post("/attandance/create")
async def cretae_attandances(
    type: AttType,
    form_datas: List[NewAttandance],
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst']:
        for form_data in form_datas:
            await makeDavomat(form_data.user_id, form_data.plant_id, type, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), usr.name, db)
        return HTTPException(status_code=200, detail=f"Ma'lumotlar saqlandi!")
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")  
    
    

@attandance_router.get("/attandance/users")
async def get_attandance_user(
    search: Optional[str] = "",
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst']:
        
        users = db.query(User).options(
            joinedload(User.last_attandance.and_(func.date(Attandance.datetime)==date.today())),
            joinedload(User.plant_users).subqueryload(Plant_User.plant)
        ).filter(
            User.disabled==False
        )
        
        
        
        if len(search) > 0:

            users = users.filter(
            or_(
                User.name.like(f"%{tarjima(search, 'ru')}%"),
                User.name.like(f"%{tarjima(search, 'uz')}%"),
            )
        )
        
        return users.order_by(User.name.asc()).all()
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")  


@attandance_router.post("/attandance/face-id", include_in_schema=False)
async def get_attandance_users_list(
    req: Request,
    db:Session = ActiveSession,
):   
    
    try:
        data  = await req.body()
        data_str = data.decode()
        data_str = data_str.split("\n",3)[3]
        data_str = data_str[:-20]

        # with open(f"{uuid.uuid4()}.json", "w") as f:
        #     f.write(data_str)
        
        data_dict = json.loads(data_str)
        AccessControllerEvent = data_dict['AccessControllerEvent']
        user_id = AccessControllerEvent['employeeNoString']
        attendanceStatus = AccessControllerEvent['attendanceStatus']
        deviceName = AccessControllerEvent['deviceName']

       

        date_str = data_dict['dateTime']
        date_obj = datetime.fromisoformat(date_str[:-6])  # remove timezone offset
        formatted_date = date_obj.strftime("%Y-%m-%d %H:%M:%S")

        if attendanceStatus == 'checkIn':
            type = 'entry'
        else:
            type = 'exit'

        if attendanceStatus:

            await makeDavomat(user_id, 0, type, formatted_date, deviceName, db)

            return "success"
    except Exception as e:
        print(e)

