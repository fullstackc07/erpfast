import uuid
import shutil
import os
from os.path import exists
from fastapi import Body, File, HTTPException, APIRouter, Depends, UploadFile
from typing import Optional, List
from security.auth import get_current_active_user
from databases.main import ActiveSession
from sqlalchemy.orm import Session

from ..models.plant_cycle import Plant_Cycle
from ..schemas.product_cycle import NewProduct_Cycle
from ..functions.product_cycle import create_product_cycle
from ..schemas.user import NewUser
from ..models.product import *
from ..models.product_store import *
from ..functions.product import *
from ..schemas.product import *
from ..models.production_tree import *
from pydantic import BaseModel


class ClonProduct(BaseModel):
    size1: Optional[str] = ""
    size2: Optional[str] = ""
    size3: Optional[str] = ""


product_router = APIRouter(tags=['Product Endpoint'])


# @product_router.get("/add_bolyasina", description="This router returns list of the products using pagination")
# async def get_products_list(
#     db: Session = ActiveSession,
#     usr: NewUser = Depends(get_current_active_user)
# ):
#     for n in range(1, 108):
#         old_logo_path = f"assets/products/{n}.png"
#         if exists(old_logo_path):

#             if n < 10:
#                 name = f"Б00{n}"
#             elif n < 100:
#                 name = f"Б0{n}"
#             else:
#                 name = f"Б{n}"


#             db.add(
#                 Product(
#                     name=name,
#                     product_type_id=8,
#                     image=f"{n}.png",
#                     unit=True,
#                     olchov_id=2
#                 )
#             )

#         db.commit()


@product_router.get("/products", description="This router returns list of the products using pagination")
async def get_products_list(
    disabled: Optional[bool] = False,
    product_type_id: Optional[int] = 0,
    search: Optional[str] = "",
    page: int = 1,
    limit: int = 10,
    db: Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if not usr.role in ['any_role']:
        return get_all_products(disabled, product_type_id, search, page, limit, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")


@product_router.get("/product_type_one", description="This router returns list of the products using pagination")
async def get_products_list_one(
    id: int,
    db: Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if not usr.role in ['any_role']:
        return get_one_product_type(id, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")


@product_router.get("/product_one", description="This router returns list of the products using pagination")
async def get_products_list(
    id: int,
    db: Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if not usr.role in ['any_role']:
        return get_one_product(id, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")


@product_router.get("/next_product_cycle_plants")
async def get_products_list(
    id: int,
    db: Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if not usr.role in ['any_role']:
        product_cycle = db.query(Product_Cycle).get(id)
        if product_cycle:
            next_pc = db.query(Product_Cycle).filter_by(
                product_id=product_cycle.product_id,
                disabled=False,
            ).filter(Product_Cycle.ordinate > product_cycle.ordinate)\
                .order_by(Product_Cycle.ordinate.asc()).first()

            if next_pc:
                return db.query(Plant).select_from(Plant_Cycle).join(Plant_Cycle.plant).filter(Plant_Cycle.cycle_id == next_pc.cycle_id, Plant_Cycle.disabled == False).group_by(Plant_Cycle.plant_id).all()
            else:
                return []
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")


@product_router.post("/product/create", description="This router is able to add new product")
async def create_new_product(
    name: str = Body(...),
    image: UploadFile = File(...),
    olchov_id: int = Body(...),
    product_type_id: int = Body(...),
    unit: bool = Body(...),
    plant_price: float = Body(..., ge=0),
    trade_price: float = Body(..., ge=0),
    alarm_value: float = Body(..., ge=0),
    db: Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst']:

        olchov = db.query(Olchov).filter_by(id=olchov_id).first()

        if not olchov:
            raise HTTPException(
                status_code=400, detail="O`lchov birligi topilmadi!")

        if product_type_id > 0:

            product_type = db.query(Product_Type).filter_by(
                id=product_type_id).first()

            if not product_type:
                raise HTTPException(
                    status_code=400, detail="Mahsulot turi topilmadi!")

        if not image.content_type in ["image/png", "image/jpg", "image/jpeg", "image/heif"]:
            raise HTTPException(
                status_code=400, detail="Rasm formati .jpg, .png yoki .jpeg bo`lishi kerak!")

        image_contents = await image.read()

        image.filename = f"{uuid.uuid4()}__{image.filename}"

        if len(image_contents) > 3000000:
            raise HTTPException(
                status_code=400, detail="Rasm hajmi ko`pi bilan 3MB bo`lmog`i darkor!")

        with open(f"assets/products/{image.filename}", "wb") as f:
            f.write(image_contents)

        unique_name = db.query(Product).filter_by(
            name=name, product_type_id=product_type_id).first()

        if unique_name:
            raise HTTPException(status_code=400, detail="Bu nom band!")

        new_product = Product(
            name=name,
            product_type_id=product_type_id,
            unit=unit,
            image=image.filename,
            trade_price=trade_price,
            plant_price=plant_price,
            alarm_value=alarm_value,
            olchov_id=olchov_id,
        )

        db.add(new_product)
        db.commit()

        raise HTTPException(status_code=200, detail="Ma`lumotlar saqlandi!")
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")


@product_router.put("/product/{id}/update", description="This router is able to update product")
async def update_one_product(
    id: int,
    name: str = Body(...),
    image: Optional[UploadFile] = File(False),
    olchov_id: int = Body(...),
    plant_price: float = Body(..., ge=0),
    trade_price: float = Body(..., ge=0),
    alarm_value: float = Body(..., ge=0),
    disabled: bool = Body(...),
    product_type_id: int = Body(...),
    unit: bool = Body(...),
    db: Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst', 'seller_admin']:

        product = db.query(Product).filter(Product.id == id)
        this_product = product.first()
        if this_product:

            olchov = db.query(Olchov).filter_by(id=olchov_id).first()

            if not olchov:
                raise HTTPException(
                    status_code=400, detail="O`lchov birligi topilmadi!")

            if image:
                if not image.content_type in ["image/png", "image/jpg", "image/jpeg", "image/heif"]:
                    raise HTTPException(
                        status_code=400, detail="Rasm formati .jpg, .png yoki .jpeg bo`lishi kerak!")

                image_contents = await image.read()

                image.filename = f"{uuid.uuid4()}__{image.filename}"
                file_name = image.filename

                if len(image_contents) > 3000000:
                    raise HTTPException(
                        status_code=400, detail="Rasm hajmi ko`pi bilan 3MB bo`lmog`i darkor!")

                with open(f"assets/products/{image.filename}", "wb") as f:
                    f.write(image_contents)

                old_logo_path = f"assets/products/{this_product.image}"

                if exists(old_logo_path):
                    os.unlink(old_logo_path)

            else:
                file_name = this_product.image

            unique_name = db.query(Product).filter_by(name=name, product_type_id=product_type_id).filter(
                Product.name != this_product.name, Product.disabled == False, Product.product_type_id == this_product.product_type_id).first()

            if unique_name:
                raise HTTPException(status_code=400, detail="Bu nom band!")

            product.update({
                Product.name: name,
                Product.image: file_name,
                Product.disabled: disabled,
                Product.olchov_id: olchov_id,
                Product.product_type_id: product_type_id,
                Product.unit: unit,
                Product.plant_price: plant_price,
                Product.trade_price: trade_price,
                Product.alarm_value: alarm_value,
            })

       
            db.commit()

            raise HTTPException(status_code=200, detail="O`zgarish saqlandi!")
        else:
            raise HTTPException(status_code=400, detail="So`rovda xatolik!")
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")

@product_router.put("/product_store/{product_store_id}/update", description="This router is able to update product")
async def update_one_product(
    product_store_id: int,
    image: Optional[UploadFile] = File(False),
    trade_price: float = Body(..., ge=0),
    db: Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst', 'seller_admin']:

        product_store_one = db.query(Product_Store).get(product_store_id)

        if product_store_one:
            if image:
                if not image.content_type in ["image/png", "image/jpg", "image/jpeg", "image/heif"]:
                    raise HTTPException(
                        status_code=400, detail="Rasm formati .jpg, .png yoki .jpeg bo`lishi kerak!")

                image_contents = await image.read()

                image.filename = f"{uuid.uuid4()}__{image.filename}"
                file_name = image.filename

                if len(image_contents) > 3000000:
                    raise HTTPException(
                        status_code=400, detail="Rasm hajmi ko`pi bilan 3MB bo`lmog`i darkor!")

                with open(f"assets/products/{image.filename}", "wb") as f:
                    f.write(image_contents)

                old_logo_path = f"assets/products/{product_store_one.product.image}"

                if exists(old_logo_path):
                    os.unlink(old_logo_path)

                db.query(Product).filter_by(id=product_store_one.product_id).update({
                    Product.image: file_name,
                })


        db.query(Product_Store).filter(
            Product_Store.product_id==product_store_one.product_id,
            Product_Store.material_id==product_store_one.material_id,
            Product_Store.market_id==product_store_one.market_id,
            Product_Store.trade_id==product_store_one.trade_id,
            Product_Store.size1==product_store_one.size1,
            Product_Store.size2==product_store_one.size2,
        ).update({Product_Store.trade_price:trade_price})

        db.commit()

        return 'success'

    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")


def copy_data_of_product(product, toProduct,  db: Session):

    db.query(Cycle).filter_by(product_id=toProduct.id).update(
        {Cycle.disabled: True})
    for cycle in toProduct.cycles:
        db.query(User_Kpi).filter_by(cycle_id=cycle.id).update(
            {User_Kpi.disabled: True})
        db.query(Plant_Cycle).filter_by(cycle_id=cycle.id).update(
            {Plant_Cycle.disabled: True})
        db.query(Component).filter_by(cycle_id=cycle.id).update(
            {Component.disabled: True})
        for component in cycle.components:
            db.query(Component_Item).filter_by(component_id=component.id).update(
                {Component_Item.disabled: True})

    for cycle in product.cycles:
        if cycle.disabled == False:
            new_cycle = Cycle(
                name=cycle.name,
                product_id=toProduct.id,
                kpi=cycle.kpi,
                ordinate=cycle.ordinate,
                spending_minut=cycle.spending_minut,
                plan_value=cycle.plan_value,
                plan_day=cycle.plan_day,
            )

            db.add(new_cycle)
            db.flush()

            for user_kpi in cycle.user_kpis:
                if cycle.disabled == False:
                    new_user_kpi = User_Kpi(
                        user_id=user_kpi.user_id,
                        cycle_id=new_cycle.id,
                        value=user_kpi.value,
                    )

                    db.add(new_user_kpi)

            for plant_cycle in cycle.plant_cycles:
                if plant_cycle.disabled == False:
                    new_plant_cycle = Plant_Cycle(
                        cycle_id=new_cycle.id,
                        plant_id=plant_cycle.plant_id,
                    )

                    db.add(new_plant_cycle)

                    db.commit()

            for component in cycle.components:
                if component.disabled == False:
                    new_component = Component(
                        cycle_id=new_cycle.id,
                        product_type_id=component.product_type_id,
                        material_type_id=component.material_type_id,
                    )

                    db.add(new_component)
                    db.flush()

                    for component_item in component.component_items:
                        if component_item.disabled == False:
                            new_component_item = Component_Item(
                                material_id=component_item.material_id,
                                product_id=component_item.product_id,
                                component_id=new_component.id,
                                value=component_item.value,
                                main=component_item.main,
                            )

                            db.add(new_component_item)


@product_router.post("/product/clonize", description="This router is able to add new product")
async def create_new_product(
    id: int,
    name: str,
    form_datas: List[ClonProduct],
    db: Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst']:

        product = db.query(Product).filter_by(id=id).first()

        if not product:
            raise HTTPException(
                status_code=400, detail="Mahsulot birligi topilmadi!")

        root_path = os.path.abspath(os.path.join(
            os.getcwd(), ".")) + "/assets/products/"
        src = f"{root_path}{product.image}"
        file_extension = os.path.splitext(src)[1]

        for form_data in form_datas:
            filename = str(uuid.uuid4()) + file_extension
            dst = f"{root_path}{filename}"

            if form_data.size1 or form_data.size2 or form_data.size3:
                newname = name
                newname += ""
                if form_data.size1:
                    newname += f"{form_data.size1}"
                if form_data.size2:
                    newname += f"x{form_data.size2}"
                if form_data.size3:
                    newname += f"x{form_data.size3}"
                newname += ""

            if exists(src):
                shutil.copyfile(src, dst)

            new_product = Product(
                name=newname,
                product_type_id=product.product_type_id,
                image=filename,
                unit=product.unit,
                olchov_id=product.olchov_id,
                plant_price=product.plant_price,
                trade_price=product.trade_price,
                alarm_value=product.alarm_value,
            )

            db.add(new_product)
            db.flush()

            copy_data_of_product(product, new_product, db)

        db.commit()

        raise HTTPException(status_code=200, detail="Ma`lumotlar saqlandi!")
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")


@product_router.post("/product/clonize/cycles", description="This router is able to add new product")
async def create_new_product(
    from_product_id: int,
    to_product_id: int,
    db: Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst']:

        product = db.query(Product).filter_by(id=from_product_id).first()

        if not product:
            raise HTTPException(
                status_code=400, detail="Mahsulot birligi topilmadi!")

        to_product = db.query(Product).filter_by(id=to_product_id).first()

        if not to_product:
            raise HTTPException(
                status_code=400, detail="Mahsulot birligi topilmadi!")

        copy_data_of_product(product, to_product, db)

        db.commit()

        raise HTTPException(status_code=200, detail="Ma`lumotlar saqlandi!")
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")


@product_router.post("/product/make_tree", description="This router is able to add new product")
async def create_new_product_tree(
    product_id: int,
    db: Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['admin', 'accountant', 'analyst']:

        product = db.query(Product).get(product_id)

        if not product:
            raise HTTPException(
                status_code=400, detail="Mahsulot topilmadi!")

        # for product in db.query(Product).filter(Product.disabled==False).offset(1550).limit(50).all():

        return create_tree(product, usr, db)
    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")


@product_router.get("/component_calculation", description="This router is able to add new product")
async def create_new_product(
    product_id: int,
    material_id: int,
    db: Session = ActiveSession,
    usr: NewUser = Depends(get_current_active_user)
):
    if usr.role in ['seller', 'seller_admin']:

        product = db.query(Product).filter_by(id=product_id).first()

        if not product:
            raise HTTPException(
                status_code=400, detail="Mahsulot topilmadi!")

        material = db.query(Material).filter_by(id=material_id).first()

        if not material:
            raise HTTPException(
                status_code=400, detail="Homashyo topilmadi!")

        return db.query(func.sum(Component.value*Production_Tree.value*material.price)).select_from(Production_Tree)\
            .join(Product, Product.id == Production_Tree.product_id)\
            .join(Product.product_cycles).join(Product_Cycle.cycle).join(Cycle.components)\
            .filter(
                Production_Tree.for_product_id == product_id,
                Component.disabled == False,
                Cycle.disabled == False,
                Product_Cycle.disabled == False,
                Component.material_type_id == material.material_type_id
        ).scalar()

    else:
        raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")
    


# @product_router.get("/clone_tp", description="This router is able to add new product")
# async def create_new_product(
#     db: Session = ActiveSession,
#     usr: NewUser = Depends(get_current_active_user)
# ):
#     if usr.role in ['admin']:

        # products = db.query(Product).filter_by(product_type_id=8, disabled=False).all()

        # for pr in products:
        #     root_path = os.path.abspath(os.path.join(
        #     os.getcwd(), ".")) + "/assets/products/"
        #     src = f"{root_path}{pr.image}"
        #     file_extension = os.path.splitext(src)[1]

        #     filename = str(uuid.uuid4()) + file_extension
        #     dst = f"{root_path}{filename}"

        #     if exists(src):
        #         shutil.copyfile(src, dst)


        #     code = str(pr.name).replace("Б", "")
        #     code_int = int(code)
        #     new_code = f"С{code}"

        #     new_product = Product(
        #         name=new_code,
        #         product_type_id=14,
        #         image=filename,
        #         unit=True,
        #         olchov_id=pr.olchov_id,
        #         plant_price=0,
        #         trade_price=0,
        #         alarm_value=0,
        #     )
        #     db.add(new_product)
        #     db.commit()

        #     if code_int >= 51 and code_int <= 65:
        #         cycle_ids = [60, 21]
        #     else:
        #         cycle_ids = [20, 21]


        #     for cyc_id in cycle_ids:

        #         new_pr_cyc_form = NewProduct_Cycle(
        #             cycle_id=cyc_id,
        #             product_id=new_product.id
        #         )

        #         create_product_cycle(new_pr_cyc_form, usr, db)


        #     create_tree(new_product, usr, db)


        # db.commit()
        

        # return 'success'            

           
            


    # else:
    #     raise HTTPException(status_code=400, detail="Sizga ruxsat berilmagan!")
