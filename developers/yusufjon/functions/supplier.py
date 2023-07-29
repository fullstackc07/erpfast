import math
from sqlalchemy import or_
from sqlalchemy.orm import joinedload, Session
from fastapi import HTTPException
from developers.yusufjon.models.material import Material
from developers.yusufjon.models.phone import Phone
from developers.yusufjon.models.supplier import *

def get_all_suppliers(search, page, limit, usr, db: Session):
    if page == 1 or page < 1:
        offset = 0
    else:
        offset = (page-1) * limit
    
    suppliers = db.query(Supplier).filter_by(disabled=False).options(
        joinedload(Supplier.phones).load_only(Phone.number)
    ).outerjoin(Supplier.phones).group_by(Supplier.id)
    

    if len(search) > 0:
        suppliers = suppliers.filter(
            or_(
                Supplier.name.like(f"%{search}%"),
                Supplier.balance.like(f"%{search}%"),
                Phone.number.like(f"%{search}%"),
            )
        )

    all_data = suppliers.order_by(Supplier.id.desc()).offset(offset).limit(limit)
    count_data = suppliers.count()

    return {
        "data": all_data.all(),
        "page_count": math.ceil(count_data / limit),
        "data_count": count_data,
        "current_page": page,
        "page_limit": limit,
    }

def create_supplier(form_data, usr, db: Session):

    unique_name = db.query(Supplier).filter_by(name=form_data.name).first()

    if unique_name:
        raise HTTPException(status_code=400, detail="Bu nom band!")
    
    new_supplier = Supplier(
        name=form_data.name,
        balance=form_data.balance,
    )
    db.add(new_supplier)
    db.flush()

    for sp_mat in form_data.materials:
        material = db.query(Material).filter_by(id=sp_mat.material_id).first()
        if not material:
            raise HTTPException(status_code=400, detail="Material topilmadi.")
        
        

    for sp_phone in form_data.phones:
        
        db.add(Phone(
            owner_id=new_supplier.id,
            number=sp_phone.number,
            ownerType="supplier"
        ))

    db.commit()

    raise HTTPException(status_code=200, detail="Ma`lumotlar saqlandi!")

def update_supplier(id, form_data, usr, db: Session):
    supplier = db.query(Supplier).filter(Supplier.id == id)
    this_supplier = supplier.first()
    if this_supplier:

        unique_name = db.query(Supplier).filter_by(name=form_data.name).filter(Supplier.name != form_data.name).first()

        if unique_name:
            raise HTTPException(status_code=400, detail="Bu nom band!")

        supplier.update({
            Supplier.name: form_data.name,
        })

        for sp_mat in form_data.materials:
            material = db.query(Material).filter_by(id=sp_mat.material_id).first()
            if not material:
                raise HTTPException(status_code=400, detail="Material topilmadi.")
            

        db.query(Phone).filter_by(owner_id=this_supplier.id, ownerType="supplier").delete()

        for sp_phone in form_data.phones:
            
            db.add(Phone(
                owner_id=this_supplier.id,
                number=sp_phone.number,
                ownerType="supplier"
            ))

        db.commit()

        raise HTTPException(status_code=200, detail="Ma`lumotlar saqlandi!")
    else:
        raise HTTPException(status_code=400, detail="So`rovda xatolik!")
    
