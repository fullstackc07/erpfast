import math
from sqlalchemy.orm import joinedload, Session, load_only, aliased
from fastapi import HTTPException
from developers.yusufjon.functions.material_store import *
from developers.yusufjon.models.material_store import Material_Store
from developers.yusufjon.models.supply import *
from developers.yusufjon.models.product_cycle import *
from developers.yusufjon.models.product_store import *
from developers.yusufjon.models.cycle_store import *
from developers.yusufjon.schemas.supply import NewSupply, UpdateSupply
from sqlalchemy import func, or_
from developers.yusufjon.utils.trlatin import tarjima
from sqlalchemy.sql import label

def filter_supplies(supplies, supplier_id, material_id, product_id, usr, from_date, to_date, search) -> Session:

    supplies = supplies.filter(Supply.disabled == False)
        

    if supplier_id > 0:
        supplies = supplies.filter(Supply.supplier_id == supplier_id)

    # if plant_id > 0:
    #     supplies = supplies.filter(Supply.plant_id == plant_id)

    if material_id > 0:
        supplies = supplies.filter(Supply.material_id == material_id)

    if product_id > 0:
        supplies = supplies.filter(Supply.product_id == product_id)

    if usr.role == 'plant_admin':
        supplies = supplies.filter(Supply.user_id == usr.id)

    supplies = supplies.filter(
        func.date(Supply.created_at) >= from_date,
        func.date(Supply.created_at) <= to_date,
    )

    if len(search) > 0:
        if supplier_id == 0:
            supplies = supplies.join(Supply.supplier) \
                .filter(
                    or_(
                        Supplier.name.like(f"%{tarjima(search, 'uz')}%"),
                        Supplier.name.like(f"%{tarjima(search, 'ru')}%"),
                    )
            )

    return supplies

def get_all_supplies(supplier_id, plant_id, material_id, product_id, from_date, to_date, search, page, limit, usr, db: Session):

    if page == 1 or page < 1:
        offset = 0
    else:
        offset = (page-1) * limit

    material = db.query(Material.name).filter(
        Material.id == Supply.material_id).subquery()
    
    product_material = db.query(Material.name).filter(
       Material.id==Supply.product_material_id).limit(1).subquery()

    has_volume = db.query(Material.has_volume).filter(
        Material.id == Supply.material_id).subquery()
    
    product = db.query(func.IF(Supply.product_material_id > 0, func.CONCAT(Product.name, ' ', product_material), Product.name)).filter(
        Product.id == Supply.product_id).subquery()
    
    cycle = db.query(Cycle.name).filter_by(id=Supply.cycle_id).limit(1).subquery()


    supplies = db.query(
        Supply.id.label("supply_id"),
        Supplier.id.label("supplier_id"),
        Supplier.name.label("supplier"),
        Supply.material_id.label("material_id"),
        Supply.product_id.label("product_id"),
        label("material", func.IF(Supply.material_id > 0, material, product)),
        label("has_volume", func.IF(Supply.material_id > 0, has_volume, False)),
        label("cycle", func.IF(Supply.cycle_id > 0, cycle, None)),
        label("product_material", product_material),
        label("summa", Supply.price*Supply.value),
        Olchov.id.label("olchov_id"),
        Olchov.name.label("olchov"),
        Plant.id.label("plant_id"),
        Plant.name.label("plant"),
        User.name.label("user"),
        Supply.value,
        Supply.price,
        Supply.value,
        Supply.created_at,
    ).select_from(Supply)\
        .join(Supply.user)\
        .join(Supply.olchov)\
        .join(Supply.supplier)
    

    supplies = filter_supplies(supplies, supplier_id, material_id, product_id, usr, from_date, to_date, search)


    # Find sum price
    sum_price = filter_supplies(db.query(func.sum(Supply.price*Supply.value)), supplier_id, material_id, product_id, usr, from_date, to_date, search).scalar()

    supplies = supplies.group_by(Supply.id)

    all_data = supplies.order_by(Supply.id.desc()).offset(offset).limit(limit)
    count_data = supplies.count()

    return {
        "data": all_data.all(),
        "page_count": math.ceil(count_data / limit),
        "total_supply_cost": sum_price,
        "data_count": count_data,
        "current_page": page,
        "page_limit": limit,
    }


def create_supply(form_data: NewSupply, usr, db: Session):
    cycle_id = 0
    supplier = db.query(Supplier).filter_by(
        id=form_data.supplier_id, disabled=False).first()
    if not supplier:
        raise HTTPException(status_code=400, detail="Taminotchi topilmadi!")

    if type(form_data.plant_id).__name__ == 'int' and form_data.plant_id > 0:
        plant = db.query(Plant).filter_by(
            id=form_data.plant_id, disabled=False).first()
        if not plant:
            raise HTTPException(status_code=400, detail="Tseh topilmadi!")

    if form_data.material_id > 0:
        material = db.query(Material).filter_by(
            id=form_data.material_id, disabled=False).first()
        if not material:
            raise HTTPException(status_code=400, detail="Homashyo topilmadi!")

        # adding to store
        add_material_store(
            price=form_data.price,
            plant_id=form_data.plant_id,
            material=material,
            value=form_data.value,
            db=db
        )

        olchov_id = material.olchov_id

    elif form_data.product_cycle_id:
        product_cycle = db.query(Product_Cycle).get(form_data.product_cycle_id)
        cycle = product_cycle.cycle
        if cycle:
            cycle_id = cycle.id
            olchov_id = product_cycle.product.olchov_id
            new_cycle_store = Cycle_Store(
                cycle_id=cycle.id,
                product_id=product_cycle.product_id,
                material_id=form_data.product_material_id,
                plant_id=form_data.plant_id,
                ordinate=product_cycle.ordinate,
                value=form_data.value,
                olchov_id=product_cycle.product.olchov_id,
                price=form_data.price,
                finished=False
            )

            db.add(new_cycle_store)
            db.commit()

    elif form_data.product_id > 0:
        product = db.query(Product).filter_by(
            id=form_data.product_id, disabled=False).first()
        if not product:
            raise HTTPException(status_code=400, detail="Mahsulot topilmadi!")
        
        product_store = db.query(Product_Store).filter_by(
            product_id=product.id,
            price=form_data.price,
            material_id=form_data.product_material_id,
            trade_id=0,
            trade_item_id=0,
            market_id=0,
        )

        product_store_one = product_store.first()

        if product_store_one:

            product_store.update(
                {Product_Store.value: Product_Store.value + form_data.value})
        else:
            new_product_store = Product_Store(
                product_id=product.id,
                price=form_data.price,
                trade_id=0,
                trade_item_id=0,
                material_id=form_data.product_material_id,
                value=form_data.value
            )
            db.add(new_product_store)

        olchov_id = product.olchov_id

    else:
        raise HTTPException(
            status_code=400, detail="Ikkisidan birini tanlang!")
    


    new_supply = Supply(
        material_id=form_data.material_id,
        product_id=form_data.product_id,
        product_material_id=form_data.product_material_id,
        cycle_id=cycle_id,
        supplier_id=form_data.supplier_id,
        value=form_data.value,
        price=form_data.price,
        olchov_id=olchov_id,
        plant_id=form_data.plant_id,
        user_id=usr.id,
    )

    db.add(new_supply)

    db.query(Supplier).filter_by(id=form_data.supplier_id).update({
        Supplier.balance: Supplier.balance +
        round(form_data.value*form_data.price)
    })

    db.commit()

    raise HTTPException(status_code=200, detail=f"Ma`lumotlar saqlandi!")


def update_supply(id, form_data: UpdateSupply, usr, db: Session):

    supply = db.query(Supply).filter(Supply.id == id, Supply.disabled == False)
    this_supply = supply.first()
    if this_supply:

        supplier = db.query(Supplier).filter_by(
            id=form_data.supplier_id, disabled=False).first()
        if not supplier:
            raise HTTPException(
                status_code=400, detail="Taminotchi topilmadi!")

        material = db.query(Material).filter_by(
            id=form_data.material_id, disabled=False).first()
        if not material:
            raise HTTPException(status_code=400, detail="Homashyo topilmadi!")

        if form_data.plant_id > 0:
            plant = db.query(Plant).filter_by(
                id=form_data.plant_id, disabled=False).first()
            if not plant:
                raise HTTPException(status_code=400, detail="Tseh topilmadi!")

        material_store = db.query(Material_Store).filter_by(
            plant_id=this_supply.plant_id,
            material_id=this_supply.material_id,
            olchov_id=this_supply.olchov_id
        )

        material_store_one = material_store.first()

        if material_store_one:

            if (material_store_one.value - this_supply.value + form_data.value) < 0:
                raise HTTPException(
                    status_code=400, detail="Homashyo allaqachon ishlatib yuborilgan!")

            material_store.update({
                Material_Store.value: Material_Store.value - this_supply.value + form_data.value
            })

            db.commit()

            db.query(Supplier).filter_by(id=supplier.id).update({
                Supplier.balance: Supplier.balance -
                round(this_supply.value*this_supply.price) +
                round(form_data.value*form_data.price)
            })

            db.commit()

            supply.update({
                Supply.material_id: form_data.material_id,
                Supply.supplier_id: form_data.supplier_id,
                Supply.value: form_data.value,
                Supply.olchov_id: material.olchov_id,
                Supply.price: form_data.price,
                Supply.plant_id: form_data.plant_id,
            })

            db.commit()

            raise HTTPException(status_code=200, detail="O`zgarish saqlandi!")
        else:
            raise HTTPException(
                status_code=400, detail="Homashyo omborda topilmadi!")
    else:
        raise HTTPException(status_code=400, detail="So`rovda xatolik!")


def delete_supply(id, db: Session):
    supply = db.query(Supply).filter(Supply.id == id, Supply.disabled == False)
    this_supply = supply.first()
    if this_supply:

        material_store = db.query(Material_Store).filter_by(
            plant_id=this_supply.plant_id,
            material_id=this_supply.material_id,
            olchov_id=this_supply.olchov_id
        )

        material_store_one = material_store.first()

        if material_store_one:

            if material_store_one.value < this_supply.value:
                raise HTTPException(
                    status_code=400, detail="Homashyo allaqachon ishlatib yuborilgan!")

            material_store.update({
                Material_Store.value: Material_Store.value - this_supply.value
            })

            db.query(Supplier).filter_by(id=this_supply.supplier_id).update({
                Supplier.balance: Supplier.balance -
                round(this_supply.value*this_supply.price)
            })

            supply.update({Supply.disabled: True})

        db.commit()

        raise HTTPException(status_code=200, detail="Taminot o`chirildi!")
    else:
        raise HTTPException(status_code=400, detail="So`rovda xatolik!")
