import math
from sqlalchemy.orm import joinedload, subqueryload, Session
from fastapi import HTTPException
from developers.yusufjon.models.component import *
from developers.yusufjon.models.component_item import *

def get_all_components(search, cycle_id, disabled, page, limit, usr, db: Session):
    if page == 1 or page < 1:
        offset = 0
    else:
        offset = (page-1) * limit
    
    components = db.query(Component).options(
        joinedload(Component.product_type),
        joinedload(Component.material_type),
        joinedload(Component.component_items).options(
            subqueryload(Component_Item.product),
            subqueryload(Component_Item.material),
        ),
    ).filter(Component.disabled == disabled)

    if cycle_id > 0:
        components = components.filter(Component.cycle_id==cycle_id)

    #if search:
       #components = components.filter(
           #Component.id.like(f"%{search}%"),
       #)

    limit = 100

    all_data = components.order_by(Component.id.desc()).offset(offset).limit(limit)
    count_data = components.count()

    return {
        "data": all_data.all(),
        "page_count": math.ceil(count_data / limit),
        "data_count": count_data,
        "current_page": page,
        "page_limit": limit,
    }

def create_component(form_data, usr, db):




    if form_data.type == 'product':
          

            check_product_type = db.query(Product_Type).filter_by(name=form_data.name, disabled=False).first()

            if check_product_type:
                product_type_id = check_product_type.id
            else:
                product_type = Product_Type(name=form_data.name)
                db.add(product_type)
                db.flush()
                product_type_id = product_type.id
            material_type_id = 0

    else:
        material_type = db.query(Material_Type).filter_by(
            name=form_data.name, hidden=False).first()
        
        if not material_type:
            material_type = Material_Type(name=form_data.name)
            db.add(material_type)
            db.flush()

        product_type_id = 0
        material_type_id = material_type.id

    new_component = Component(
        material_type_id=material_type_id,
        product_type_id=product_type_id,
        cycle_id=form_data.cycle_id,
        value=form_data.value,
    )
    
    db.add(new_component)
    db.commit()
    raise HTTPException(status_code=200, detail="Ma`lumotlar saqlandi!")

def update_component(id, form_data, usr, db: Session):
    component = db.query(Component).filter(Component.id == id)
    this_component = component.first()
    if this_component:

        if form_data.type == 'product':
            product_type = db.query(Product_Type).filter_by(disabled=False).first()
            if not product_type:
                check_product_type = db.query(Product_Type).filter_by(name=form_data.name, disabled=False).first()
                if check_product_type:
                    raise HTTPException(
                        status_code=400, detail="Ushbu kod band qilingan!")
                product_type = Product_Type(name=form_data.name)
                db.add(product_type)
                db.flush()
            product_type_id = product_type.id
            material_type_id = 0
        else:
            material_type = db.query(Material_Type).filter_by(
                name=form_data.name, hidden=False).first()
            if not material_type:
                material_type = Material_Type(name=form_data.name)
                db.add(material_type)
                db.flush()
            product_type_id = 0
            material_type_id = material_type.id

        check_component = db.query(Component).filter_by(
            product_type_id=product_type_id,
            material_type_id=material_type_id,
            cycle_id=form_data.cycle_id,
            disabled=False
        ).filter(Component.id != product_type_id).first()

        if check_component:
            raise HTTPException(status_code=400, detail="Ushbu tarkib mavjud!")

        component.update({    
            Component.product_type_id: product_type_id,
            Component.material_type_id: material_type_id,
            Component.cycle_id: form_data.cycle_id,
        })
        db.commit()

        raise HTTPException(status_code=200, detail="O`zgarish saqlandi!")
    else:
        raise HTTPException(status_code=400, detail="So`rovda xatolik!")
    
def delete_component(id,db):
        check_component = db.query(Component).filter(Component.id == id).first()
        if check_component:
            db.query(Component).filter_by(id = id).update({Component.disabled: True})
            db.commit()
            raise HTTPException(status_code=200, detail="O'chirildi !")
        else:
            raise HTTPException(status_code=400, detail="Topilmadi !")