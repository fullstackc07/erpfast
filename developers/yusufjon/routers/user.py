import uuid
from fastapi import Body, File, UploadFile
from developers.yusufjon.models.holiday import Holiday
from developers.yusufjon.models.phone import Phone
from developers.yusufjon.models.plant import Plant
from developers.yusufjon.models.plant_user import Plant_User
from developers.yusufjon.models.user import *
from developers.yusufjon.functions.user import *
from developers.yusufjon.schemas.plant_cycle import *
from developers.yusufjon.schemas.user import *
from developers.abdusamad.models import Markets
from security.auth import get_password_hash
from os.path import exists
import os
from sqlalchemy.orm import joinedload, subqueryload, contains_eager

from developers.yusufjon.utils.main import *
user_router = APIRouter(tags=['User Endpoint'])

def unique(list1) -> list:
 
    # initialize a null list
    unique_list = []
 
    # traverse for all elements
    for x in list1:
        # check if exists in unique_list or not
        if x not in unique_list:
            unique_list.append(x)

    return unique_list

@user_router.get("/users", description="This router returns list of the users using pagination")
async def get_users_list(
    search: Optional[str] = "",
    role: Optional[str] = None,
    page: int = 1,
    disabled: Optional[bool] = False,
    # balance: Optional[any] = 0,
    limit: int = 10,
    db: Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user),
    market_id: Optional[int] = 0
):
    if usr.role in ['admin', 'analyst', 'accountant', 'seller_admin']:
        return get_all_users(role, disabled, search, page, limit, usr, db, market_id)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")


@user_router.get("/user_one", description="This router returns list of the users using pagination")
async def get_one__one_user(
    id: int,
    db: Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    try:

        if not usr.role in ['admin', 'analyst', 'accountant', 'seller_admin']:
            id = usr.id

        user = db.query(User).options(joinedload(User.holidays), joinedload(User.shift)).filter_by(id=id).first()

        if not user:
            raise HTTPException(status_code=400, detail="Hodim topilmadi!")

        user.plant_users = db.query(Plant_User).options(joinedload(Plant_User.plant)).filter(
            Plant_User.user_id == user.id, Plant_User.disabled == False).all()


        pl_ids = [pl_u.plant_id for pl_u in user.plant_users]

        # user.user_cycles = db.query(Plant_Cycle).filter(Plant_Cycle.plant_id.in_(pl_ids), Plant_Cycle.disabled == False).group_by(Plant_Cycle.cycle_id).all()

        user.market = db.query(Markets).get(user.market_id)
        return user

    except Exception as e:
        from ..bot.bot import bot
        await bot.send_message(-1001299185219, e)


@user_router.post("/user/create", description="This router is able to add new user")
async def create_new_user(
    name: str = Body(..., min_length=5),
    nation: str = Body(..., min_length=3),
    birthdate: str = Body(...),
    specialty: str = Body(..., min_length=5),
    passport: UploadFile = File(...),
    workbegindate: str = Body(...),
    salary: int = Body(..., ge=0),
    shift_id: int = Body(..., ge=0),
    salaryDay: int = Body(..., ge=1, le=31),
    agreement_expiration: str = Body(...),
    username: str = Body(..., min_length=5),
    password: str = Body(..., min_length=5),
    disabled: Optional[bool] = Body(default=False),
    phones: str = Body(""),
    role: UserRoles = Body(...),
    market_id: Optional[int] = Body(0, ge=0),
    address: Optional[str] = Body(""),
    db: Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):

    phones = phones.split(";")

    # return phones

    if usr.role in ['admin', 'analyst', 'accountant']:

        if not passport.content_type in ["image/png", "image/jpg", "image/jpeg"]:
            raise HTTPException(
                status_code=400, detail="Rasm formati .jpg, .png yoki .jpeg bo`lishi kerak!")

        passport_contents = await passport.read()

        passport.filename = f"{uuid.uuid4()}__{passport.filename}"

        if len(passport_contents) > 3000000:
            raise HTTPException(
                status_code=400, detail="Rasm hajmi ko`pi bilan 3MB bo`lmog`i darkor!")

        with open(f"assets/passports/{passport.filename}", "wb") as f:
            f.write(passport_contents)

        unique_user = db.query(User).filter_by(username=username).first()

        if unique_user:
            raise HTTPException(status_code=400, detail="Bu login band!")

        if len(password) < 8:
            raise HTTPException(
                status_code=400, detail="Parol kamida 8 ta belgidan iborat bo`lishi kerak!")

        new_user = User(
            name=name,
            nation=nation,
            birthDate=birthdate,
            specialty=specialty,
            passport=passport.filename,
            workBeginDate=workbegindate,
            agreement_expiration=agreement_expiration,
            disabled=disabled,
            role=role,
            salaryDay=salaryDay,
            shift_id=shift_id,
            salary=salary,
            username=username,
            market_id=market_id,
            address=address,
            passwordHash=get_password_hash(password)
        )

        db.add(new_user)
        db.flush()

        for ph in phones:
            db.add(Phone(
                number=ph,
                owner_id=new_user.id,
                ownerType="user"
            ))

        db.commit()

        raise HTTPException(status_code=200, detail="Ma`lumotlar saqlandi!")

    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")


@user_router.put("/user/{id}/update", description="This router is able to update user")
async def update_one_user(
    id: int,
    name: str = Body(..., min_length=5),
    nation: str = Body(..., min_length=3),
    birthdate: str = Body(...),
    specialty: str = Body(..., min_length=5),
    passport: Optional[UploadFile] = File(False),
    workbegindate: str = Body(...),
    agreement_expiration: str = Body(...),
    username: str = Body(..., min_length=5),
    salaryDay: int = Body(..., ge=1, le=31),
    password: Optional[str] = Body(""),
    disabled: Optional[bool] = Body(default=False),
    role: UserRoles = Body(...),
    shift_id: int = Body(..., ge=0),
    market_id: Optional[int] = Body(0, ge=0),
    address: Optional[str] = Body(""),
    phones: str = Body(""),
    salary: int = Body(..., ge=0),
    db: Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'analyst', 'accountant', 'seller_admin']:

        phones = phones.split(";")

        user = db.query(User).filter_by(id=id)
        this_user = user.first()

        if not this_user:
            raise HTTPException(status_code=400, detail="Hodim topilmadi!")

        if passport:
            # raise HTTPException(status_code=400, detail=f"{passport.content_type}")

            if not passport.content_type in ["image/png", "image/jpg", "image/jpeg"]:
                raise HTTPException(
                    status_code=400, detail="Rasm formati .jpg, .png yoki .jpeg bo`lishi kerak!")

            passport_contents = await passport.read()

            passport.filename = f"{uuid.uuid4()}__{passport.filename}"
            file_name = passport.filename

            if len(passport_contents) > 5000000:
                raise HTTPException(
                    status_code=400, detail="Rasm hajmi ko`pi bilan 3MB bo`lmog`i darkor!")

            with open(f"assets/passports/{passport.filename}", "wb") as f:
                f.write(passport_contents)

            if len(this_user.passport) > 0:
                old_logo_path = f"assets/passports/{this_user.passport}"

                if exists(old_logo_path):
                    os.unlink(old_logo_path)
        else:
            file_name = this_user.passport

        unique_user = db.query(User).filter_by(username=username).filter(
            User.username != this_user.username).first()

        if unique_user:
            raise HTTPException(status_code=400, detail="Bu login band!")

        if len(password) > 0:
            if len(password) < 8:
                raise HTTPException(
                    status_code=400, detail="Parol kamida 8 ta belgidan iborat bo`lishi kerak!")
            password = get_password_hash(password)
        else:
            password = this_user.passwordHash

        user.update({
            User.name: name,
            User.nation: nation,
            User.birthDate: birthdate,
            User.specialty: specialty,
            User.passport: file_name,
            User.workBeginDate: workbegindate,
            User.agreement_expiration: agreement_expiration,
            User.disabled: disabled,
            User.role: role,
            User.salary: salary,
            User.salaryDay: salaryDay,
            User.shift_id: shift_id,
            User.username: username,
            User.passwordHash: password,
            User.market_id: market_id,
            User.address: address
        })

        for ph in this_user.phones:
            db.query(Phone).filter_by(id=ph.id).delete()

        for ph in phones:
            db.add(Phone(
                number=ph,
                owner_id=this_user.id,
                ownerType="user"
            ))

        db.commit()

        raise HTTPException(status_code=200, detail="Ma`lumotlar saqlandi!")

    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")



@user_router.get("/get_working_days", description="This router is able to update user")
async def get_working_days(
    year: int,
    month: int,
    usr: NewUser = Depends(get_current_active_user)
):

    return calcWorkingDays(year, month, usr)
    
    


@user_router.put("/update_profile/{id}", description="This router is able to update user")
async def update_one_user(
    id: int,
    name: str = Body(..., min_length=5),
    username: str = Body(..., min_length=5),
    password: Optional[str] = Body(""),
    db: Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if not usr.role in ['any']:

        id = usr.id
        user = db.query(User).filter_by(id=id)
        this_user = user.first()

        if not this_user:
            raise HTTPException(status_code=400, detail="Hodim topilmadi!")

        unique_user = db.query(User).filter_by(username=username).filter(
            User.username != this_user.username).first()

        if unique_user:
            raise HTTPException(status_code=400, detail="Bu login band!")

        if len(password) > 0:
            if len(password) < 8:
                raise HTTPException(
                    status_code=400, detail="Parol kamida 8 ta belgidan iborat bo`lishi kerak!")
            password = get_password_hash(password)
        else:
            password = this_user.passwordHash

        user.update({
            User.name: name,
            User.username: username,
            User.passwordHash: password
        })

        db.commit()

        raise HTTPException(status_code=200, detail="Ma`lumotlar saqlandi!")

    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")


@user_router.post("/create_holiday/{id}", description="This router is able to update user")
async def create_holiday(
    id: int,
    weekdays: List[Optional[str]],
    db: Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'analyst', 'accountant']:
        user = db.query(User).get(id)

        if not user:
            raise HTTPException(status_code=400, detail="Hodim topilmadi!")

        db.query(Holiday).filter_by(user_id=id).delete()

        for day in unique(weekdays):
            if day not in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
                raise HTTPException(
                    status_code=400, detail="Hafta Kuni noto`g`ri")

            db.add(Holiday(
                user_id=user.id,
                week_day=day
            ))

        db.commit()

        raise HTTPException(status_code=200, detail="Ma`lumotlar saqlandi!")

    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")
