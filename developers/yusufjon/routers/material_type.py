import os
import uuid
from fastapi import Body, File, HTTPException, APIRouter, Depends, UploadFile
from typing import Optional
from developers.yusufjon.schemas.user import NewUser
from security.auth import get_current_active_user
from databases.main import ActiveSession
from sqlalchemy.orm import joinedload, Session
from developers.yusufjon.models.material_type import *
from developers.yusufjon.functions.material_type import *
from developers.yusufjon.schemas.material_type import *
from os.path import exists

material_type_router = APIRouter(tags=['Material_Type Endpoint'])

@material_type_router.get("/material_types", description="This router returns list of the material_types using pagination")
async def get_material_types_list(
    search: Optional[str] = "",
    hidden: Optional[bool] = False,
    for_plant_id: Optional[int] = 0,
    page: int = 1,
    limit: int = 10,
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):   
    if not usr.role in ['any_role']:
        return get_all_material_types(for_plant_id, search, page, limit, usr, db, hidden)  
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")  

@material_type_router.post("/material_type/create", description="This router is able to add new material_type")
async def create_new_material_type(
    name: str = Body(...),
    olchov_id: int = Body(...),
    image: UploadFile = File(...),
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst']:

        if not image.content_type in ["image/png", "image/jpg", "image/jpeg", "image/heic"]:
            raise HTTPException(status_code=400, detail="Rasm formati .jpg, .png yoki .jpeg bo`lishi kerak!")

        image_contents = await image.read()

        image.filename = f"{uuid.uuid4()}__{image.filename}"

        if len(image_contents) > 3000000:
            raise HTTPException(status_code=400, detail="Rasm hajmi ko`pi bilan 3MB bo`lmog`i darkor!")

        with open(f"assets/material_types/{image.filename}", "wb") as f:
            f.write(image_contents)

        unique_name = db.query(Material_Type).filter_by(name=name).first()

        if unique_name:
            raise HTTPException(status_code=400, detail="Bu nom band!")


        new_material_type = Material_Type(
            name=name,
            olchov_id=olchov_id,
            image=image.filename,
        )

        db.add(new_material_type)
        db.commit()

        raise HTTPException(status_code=200, detail="Ma`lumotlar saqlandi!")
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")

@material_type_router.put("/material_type/{id}/update", description="This router is able to update material_type")
async def update_one_material_type(
    id: int,
    name: str = Body(...),
    olchov_id: int = Body(...),
    image: Optional[UploadFile] = File(False),
    hidden: bool = Body(...),
    db:Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst']:

        material_type = db.query(Material_Type).filter(Material_Type.id == id)
        this_material_type = material_type.first()
        if this_material_type:
            if image:
                if not image.content_type in ["image/png", "image/jpg", "image/jpeg", "image/heic"]:
                    raise HTTPException(status_code=400, detail="Rasm formati .jpg, .png yoki .jpeg bo`lishi kerak!")

                image_contents = await image.read()

                image.filename = f"{uuid.uuid4()}__{image.filename}"
                file_name = image.filename

                if len(image_contents) > 3000000:
                    raise HTTPException(status_code=400, detail="Rasm hajmi ko`pi bilan 3MB bo`lmog`i darkor!")

                with open(f"assets/material_types/{image.filename}", "wb") as f:
                    f.write(image_contents)

                if not this_material_type.image:
                    this_material_type.image = 'popo.jpg'

                old_logo_path = f"assets/material_types/{this_material_type.image}"

                if exists(old_logo_path):
                    os.unlink(old_logo_path)
            else:
                file_name = this_material_type.image

            unique_name = db.query(Material_Type).filter_by(name=name).filter(Material_Type.name != this_material_type.name).first()

            if unique_name:
                raise HTTPException(status_code=400, detail="Bu nom band!")
       

            material_type.update({    
                Material_Type.name: name,
                Material_Type.olchov_id: olchov_id,
                Material_Type.image: file_name,
                Material_Type.hidden: hidden,
            })

            db.commit()

            raise HTTPException(status_code=200, detail="O`zgarish saqlandi!")
        else:
            raise HTTPException(status_code=400, detail="So`rovda xatolik!")
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")
