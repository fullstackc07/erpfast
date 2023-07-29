from developers.yusufjon.utils.main import *
from developers.yusufjon.models.phone import *
from developers.yusufjon.functions.phone import *
from developers.yusufjon.schemas.phone import *

phone_router = APIRouter(tags=['Phone Endpoint'])

@phone_router.get("/phones", description="This router returns list of the phones using pagination")
async def get_phones_list(
    search: Optional[List] = [],
    page: int = 1,
    limit: int = 10,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):   
    if usr.role in ['admin', 'accountant', 'analyst']:
        return get_all_phones(search, page, limit, usr, db)  
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")  

@phone_router.post("/phone/create", description="This router is able to add new phone")
async def create_new_phone(
    form_data: NewPhone,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst']:
        return create_phone(form_data, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")

@phone_router.put("/phone/{id}/update", description="This router is able to update phone")
async def update_one_phone(
    id: int,
    form_data: UpdatePhone,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst']:
        return update_phone(id, form_data, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")
