import math
from sqlalchemy import or_
from sqlalchemy.orm import joinedload, Session
from fastapi import HTTPException
from developers.yusufjon.models.component_item import *
from developers.yusufjon.utils.trlatin import tarjima


def get_all_component_items(component_id, search, disabled, page, limit, usr, db: Session):
    
    if page == 1 or page < 1:
        offset = 0
    else:
        offset = (page-1) * limit

    component_items = db.query(Component_Item).options(
        joinedload(Component_Item.product).subqueryload(Product.olchov),
        joinedload(Component_Item.material).subqueryload(Material.olchov),
    ).filter(Component_Item.component_id == component_id)\
        .filter(Component_Item.disabled == disabled)\


    if search:
        component_items = component_items.join(Component_Item.product).join(Component_Item.material).filter(
            or_(
                Material.name.like(f"%{tarjima(search, 'uz')}%"),
                Material.name.like(f"%{tarjima(search, 'ru')}%"),
                Product.name.like(f"%{tarjima(search, 'uz')}%"),
                Product.name.like(f"%{tarjima(search, 'ru')}%"),
            )
        )

    all_data = component_items.order_by(
        Component_Item.id.desc()).offset(offset).limit(limit)
    count_data = component_items.count()

    return {
        "data": all_data.all(),
        "page_count": math.ceil(count_data / limit),
        "data_count": count_data,
        "current_page": page,
        "page_limit": limit,
    }


def create_component_item(form_data, usr, db: Session):

    check_component = db.query(Component_Item).filter_by( 
        material_id=form_data.material_id,
        product_id=form_data.product_id,
        component_id=form_data.component_id,
        disabled=False,
        main=form_data.main).first()
    
    if check_component:
        raise HTTPException(status_code=400, detail="Bu tarkib mavjud !")
    
    new_component_item = Component_Item(
        material_id=form_data.material_id,
        product_id=form_data.product_id,
        component_id=form_data.component_id,
        value=form_data.value,
        main=form_data.main
    )

    if new_component_item.main == True:
        
        db.query(Component_Item).filter(Component_Item.component_id == form_data.component_id )\
            .update({Component_Item.main: False})
        
        db.add(new_component_item)
        db.commit()

    db.add(new_component_item)
    db.commit()

    raise HTTPException(status_code=200, detail="Ma`lumotlar saqlandi!")


def update_component_item(id, form_data, usr, db):
    component_item = db.query(Component_Item).filter(Component_Item.id == id)
    this_component_item = component_item.first()
    if this_component_item:
        
        if form_data.main == True:
            db.query(Component_Item).filter(Component_Item.component_id == this_component_item.component_id)\
                .update({Component_Item.main: False})
            
            db.commit()

            component_item.update({
                Component_Item.material_id: form_data.material_id,
                Component_Item.product_id: form_data.product_id,
                Component_Item.component_id: form_data.component_id,
                Component_Item.main: form_data.main,
                Component_Item.value: form_data.value,
            })   
            db.commit() 

        else:
            component_item.update({
                Component_Item.material_id: form_data.material_id,
                Component_Item.product_id: form_data.product_id,
                Component_Item.component_id: form_data.component_id,
                Component_Item.main: form_data.main,
                Component_Item.value: form_data.value,
            })   
            db.commit() 
            
        raise HTTPException(status_code=200, detail="O`zgarish saqlandi!")
    else:
        raise HTTPException(status_code=400, detail="So`rovda xatolik!")

def delete_component_item(id,db):
        check_component = db.query(Component_Item).filter(Component_Item.id == id).first()
        if check_component:
            db.query(Component_Item).filter_by(id = id).update({Component_Item.disabled: True})
            db.commit()
            raise HTTPException(status_code=200, detail="O'chirildi !")
        else:
            raise HTTPException(status_code=400, detail="Topilmadi !")