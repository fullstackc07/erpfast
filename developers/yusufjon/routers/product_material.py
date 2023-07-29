from fastapi import HTTPException, APIRouter, Depends
from typing import Optional
from developers.yusufjon.schemas.user import NewUser
from security.auth import get_current_active_user
from databases.main import ActiveSession
from sqlalchemy.orm import joinedload, Session
from developers.yusufjon.models.product_material import *
from developers.yusufjon.functions.product_material import *
from developers.yusufjon.schemas.product_material import *

product_material_router = APIRouter(tags=['Product Material'])


@product_material_router.get("/product_material", description="This router returns list of the olchovs using pagination")
async def product_material_get(
    material_id: Optional[int] = 0,
    product_id: Optional[int] = 0,
    page: int = 1,
    limit: int = 10,
    db: Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if not usr.role in ['any_role']:
        return product_material_gets(material_id, product_id, page, limit, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")


@product_material_router.post("/product_material")
async def product_material_get(
    items: SchemaPostMy,
    db: Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    '''
    ### Maxsulotga material (materialga maxsulot) biriktirish
    \n\n
    **type**: `PRODUCT` or `MATERIAL`
    \n
    **id**: `int`
    \n
    **values**: `[int]`
    '''
    if not usr.role in ['any_role']:
        return product_material_insert(items, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")

@product_material_router.delete("/product_material")
async def product_material_get(
    id: int,
    db: Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    '''
    ### Maxsulotga material (materialga maxsulot) o`chirish
    \n\n
    **id**: `int`
    \n
    '''
    if not usr.role in ['any_role']:
        return product_material_delete(id, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")
