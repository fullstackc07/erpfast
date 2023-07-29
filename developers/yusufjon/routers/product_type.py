import uuid
import os
from os.path import exists
from fastapi import Body, File, HTTPException, APIRouter, Depends, UploadFile
from typing import Optional
from developers.yusufjon.schemas.user import NewUser
from security.auth import get_current_active_user
from databases.main import ActiveSession
from sqlalchemy.orm import joinedload, Session
from developers.yusufjon.models.product_type import *
from developers.yusufjon.functions.product_type import *
from developers.yusufjon.schemas.product_type import *

product_type_router = APIRouter(tags=['Product_Type Endpoint'])

@product_type_router.get("/product_types", description="This router returns list of the product_types using pagination")
async def get_product_types_list(
    disabled: Optional[bool] = False,
    search: Optional[str] = "",
    warehouse: Optional[str] = 'all',
    plant_id: Optional[int] = 0,
    page: int = 1,
    limit: int = 10,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):   
    if not usr.role in ['any_role']:
        return get_all_product_types(disabled, plant_id, warehouse, search, page, limit, usr, db)  
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")  

@product_type_router.post("/product_type/create", description="This router is able to add new product_type")
async def create_new_product_type(
    name: str = Body(...),
    image: UploadFile = File(...),
    olchov_id: int = Body(...),
    detail: bool = Body(default=False),
    hasSize: Optional[bool] = Body(False),
    isReady: Optional[bool] = Body(False),
    number: Optional[int] = Body(0),
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst']:

        olchov = db.query(Olchov).filter_by(id=olchov_id).first()

        if not olchov:
            raise HTTPException(status_code=400, detail="O`lchov birligi topilmadi!")

        if not image.content_type in ["image/png", "image/jpg", "image/jpeg"]:
            raise HTTPException(status_code=400, detail="Rasm formati .jpg, .png yoki .jpeg bo`lishi kerak!")

        image_contents = await image.read()

        image.filename = f"{uuid.uuid4()}__{image.filename}"

        if len(image_contents) > 3000000:
            raise HTTPException(status_code=400, detail="Rasm hajmi ko`pi bilan 3MB bo`lmog`i darkor!")

        with open(f"assets/product_types/{image.filename}", "wb") as f:
            f.write(image_contents)

        unique_name = db.query(Product_Type).filter_by(name=name).first()

        if unique_name:
            raise HTTPException(status_code=400, detail="Bu nom band!")
        

        new_product_type = Product_Type(
            name=name,
            image=image.filename,
            olchov_id=olchov_id,
            hasSize=hasSize,
            number=number,
            isReady=isReady,
            detail=detail
        )

        db.add(new_product_type)
        db.commit()

        raise HTTPException(status_code=200, detail="Ma`lumotlar saqlandi!")
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")

@product_type_router.put("/product_type/{id}/update", description="This router is able to update product_type")
async def update_one_product_type(
    id: int,
    name: str = Body(...),
    image: Optional[UploadFile] = File(False),
    olchov_id: int = Body(...),
    disabled: bool = Body(...),
    detail: bool = Body(...),
    hasSize: Optional[bool] = Body(False),
    isReady: Optional[bool] = Body(False),
    number: Optional[int] = Body(0),
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst']:

        product_type = db.query(Product_Type).filter(Product_Type.id == id)
        this_product_type = product_type.first()
        if this_product_type:

            olchov = db.query(Olchov).filter_by(id=olchov_id).first()

            if not olchov:
                raise HTTPException(status_code=400, detail="O`lchov birligi topilmadi!")

            if image:
                if not image.content_type in ["image/png", "image/jpg", "image/jpeg"]:
                    raise HTTPException(status_code=400, detail="Rasm formati .jpg, .png yoki .jpeg bo`lishi kerak!")

                image_contents = await image.read()

                image.filename = f"{uuid.uuid4()}__{image.filename}"
                file_name = image.filename

                if len(image_contents) > 3000000:
                    raise HTTPException(status_code=400, detail="Rasm hajmi ko`pi bilan 3MB bo`lmog`i darkor!")

                with open(f"assets/product_types/{image.filename}", "wb") as f:
                    f.write(image_contents)
                
                if not this_product_type.image:
                    this_product_type.image = 'popo.jpg'

                old_logo_path = f"assets/product_types/{this_product_type.image}"

                if exists(old_logo_path):
                    os.unlink(old_logo_path)
            else:
                file_name = this_product_type.image

            unique_name = db.query(Product_Type).filter_by(name=name).filter(Product_Type.name != this_product_type.name, Product_Type.disabled==False).first()

            if unique_name:
                raise HTTPException(status_code=400, detail="Bu nom band!")
            
           

            product_type.update({    
                Product_Type.name: name,
                Product_Type.image: file_name,
                Product_Type.disabled: disabled,
                Product_Type.olchov_id: olchov_id,
                Product_Type.detail: detail,
                Product_Type.hasSize: hasSize,
                Product_Type.number: number,
                Product_Type.isReady: isReady,
            })

            db.commit()

            raise HTTPException(status_code=200, detail="O`zgarish saqlandi!")
        else:
            raise HTTPException(status_code=400, detail="So`rovda xatolik!")
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")
