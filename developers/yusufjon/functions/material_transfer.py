import math
from sqlalchemy.orm import joinedload, Session, aliased
from fastapi import HTTPException
from developers.yusufjon.functions.material_store import *
from developers.yusufjon.models.material_store import Material_Store
from developers.yusufjon.models.material_transfer import *
from developers.yusufjon.schemas.material_transfer import *

def get_plants_material_transfer(material_id, usr, db: Session):

    material = db.query(Material).filter_by(id=material_id, disabled=False).first()
    if not material:
        raise HTTPException(status_code=400, detail="Homashyo topilmadi!")

    plants = db.query(Material_Store).options(
        joinedload(Material_Store.plant).load_only(Plant.name),
        joinedload(Material_Store.olchov)
    ).filter(
        Material_Store.material_id == material.id,
        Material_Store.olchov_id == material.olchov_id,
        Material_Store.value > 0
    ).all()

    return plants

def get_all_material_transfers(from_date, to_date, search, material_id, plant_id, source_id, page, limit, usr, db: Session):
    
    if page == 1 or page < 1:
        offset = 0
    else:
        offset = (page-1) * limit
    
    source = aliased(Plant, name='Source')

    material_transfers = db.query(Material_Transfer,Olchov,Plant,Material, source)\
        .select_from(Material_Transfer)\
        .join(Material_Transfer.olchov)\
        .join(Material_Transfer.plant)\
        .join(source, Material_Transfer.source)\
        .join(Material_Transfer.material).filter(Material_Transfer.disabled == False)

    if material_id > 0:
         material_transfers = material_transfers.filter(Material_Transfer.material_id == material_id)
    
    if source_id > 0:
         material_transfers = material_transfers.filter(Material_Transfer.source_id == source_id)
    
    if plant_id > 0:
        material_transfers = material_transfers.filter(Material_Transfer.plant_id == plant_id)

   
    material_transfers = material_transfers.filter(
        func.date(Material_Transfer.created_at) >= from_date,
        func.date(Material_Transfer.created_at) <= to_date,
    )

    if search:


        material_transfers = material_transfers\
            .join(Material_Transfer.material)\
            .join(Material.material_type)\
            .filter(
                or_(
                    Material_Type.name.like(f"%{tarjima(search, 'ru')}%"), 
                    Material_Type.name.like(f"%{tarjima(search, 'uz')}%"), 
                    Material.name.like(f"%{tarjima(search, 'ru')}%"), 
                    Material.name.like(f"%{tarjima(search, 'uz')}%"),
                    Material_Transfer.value.like(search) 
                )
            )

    
    all_data = material_transfers.order_by(Material_Transfer.id.desc()).offset(offset).limit(limit)
    count_data = material_transfers.count()

    return {
        "data": all_data.all(),
        "page_count": math.ceil(count_data / limit),
        "data_count": count_data,
        "current_page": page,
        "page_limit": limit,
    }

def create_material_transfer(form_data: NewMaterial_Transfer, usr, db: Session):

    material = db.query(Material).filter_by(id=form_data.material_id, disabled=False).first()
    if not material:
        raise HTTPException(status_code=400, detail="Homashyo topilmadi!")
    
    if form_data.plant_id > 0:
        plant = db.query(Plant).filter_by(id=form_data.plant_id, disabled=False).first()
        if not plant:
            raise HTTPException(status_code=400, detail="Tseh topilmadi!")
        
    # materialdan ayirish
    price = substract_material_store(form_data.source_id, form_data.value, material, db)
    add_material_store(price, form_data.plant_id, material, form_data.value, db)

    new_material_transfer = Material_Transfer(
        material_id=form_data.material_id,
        source_id=form_data.source_id,
        value=form_data.value,
        plant_id=form_data.plant_id,
        olchov_id=material.olchov_id,
        price=price,
    )

    db.add(new_material_transfer)
    db.commit()

    raise HTTPException(status_code=200, detail="Ma`lumotlar saqlandi!")


def update_material_transfer(id, form_data: UpdateMaterial_Transfer, usr, db: Session):
    
    material_transfer = db.query(Material_Transfer).filter(Material_Transfer.id == id)
    this_m_transfer = material_transfer.first()
    if this_m_transfer:

        # 1 - sehda to`g`irlash
        add_material_store(material_transfer.price, this_m_transfer.source_id, this_m_transfer.material, this_m_transfer.value, db)
        price = substract_material_store(this_m_transfer.source_id, this_m_transfer.material, form_data.value, db)

        # 2 - sehda to`g`irlash
        add_material_store(price, this_m_transfer.plant_id, this_m_transfer.material, form_data.value, db)
        price = substract_material_store(this_m_transfer.plant_id, this_m_transfer.material,  this_m_transfer.value, db)

        material_transfer.update({    
            Material_Transfer.value: this_m_transfer.value,
            Material_Transfer.price: price,
        })
        db.commit()

        raise HTTPException(status_code=200, detail="O`zgarish saqlandi!")
    else:
        raise HTTPException(status_code=400, detail="So`rovda xatolik!")
    

def delete_m_transfer(id, db: Session):
    m_transfer = db.query(Material_Transfer).filter(Material_Transfer.id == id, Material_Transfer.disabled == False)
    this_m_transfer = m_transfer.first()
    if this_m_transfer:

        price = substract_material_store(this_m_transfer.plant_id, this_m_transfer.value, this_m_transfer.material, db)
        add_material_store(price, this_m_transfer.source_id, this_m_transfer.material, this_m_transfer.value, db)

        m_transfer.update({Material_Transfer.disabled: True})
        db.commit()

        raise HTTPException(status_code=200, detail="Ma`lumotlar saqlandi!")

    else:
        raise HTTPException(status_code=400, detail="So`rovda xatolik!")

