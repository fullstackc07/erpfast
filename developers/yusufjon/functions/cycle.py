from copy import copy, deepcopy
from email.policy import HTTP
import math
from sqlalchemy import or_
from sqlalchemy.orm import joinedload, Session
from fastapi import HTTPException
from developers.yusufjon.models.component import Component
from developers.yusufjon.models.component_item import Component_Item
from developers.yusufjon.models.plant_cycle import Plant_Cycle
from developers.yusufjon.models.cycle_store import Cycle_Store
from developers.yusufjon.models.cycle import *
from developers.yusufjon.models.material_type import Material_Type
from developers.yusufjon.models.product_cycle import Product_Cycle
from developers.abdusamad.models import *
from developers.yusufjon.schemas.cycle import NewCycle, UpdateCyclePosition
from developers.yusufjon.utils.trlatin import tarjima


def get_all_cycles(product_type_id, search, page, limit, usr, db: Session):

    if page == 1 or page < 1:
        offset = 0
    else:
        offset = (page-1) * limit

    cycles = db.query(Cycle).filter_by(disabled=False)

    if product_type_id > 0:
        cycles = cycles.filter_by(product_type_id=product_type_id)

    if search:
        cycles = cycles.filter(
            or_(
                Cycle.name.like(f"%{tarjima(search, 'uz')}%"),
                Cycle.name.like(f"%{tarjima(search, 'ru')}%"),
            )
        )

    all_data = cycles.order_by(
        Cycle.id.asc()).offset(offset).limit(limit)
    count_data = cycles.count()

    return {
        "data": all_data.all(),
        "page_count": math.ceil(count_data / limit),
        "data_count": count_data,
        "current_page": page,
        "page_limit": limit,
    }


def create_cycle(form_data: NewCycle, usr, db: Session):

    product_type = db.query(Product_Type).filter_by(id=form_data.product_type_id, disabled=False).first()

    if not product_type:
        raise HTTPException(status_code=400, detail="Mahsulot topilmadi!")

    unique_name = db.query(Cycle).filter_by(
        product_type_id=product_type.id, name=form_data.name, disabled=False).first()

    if unique_name:
        raise HTTPException(status_code=400, detail="Bu nomli jarayon mavjud!")

    new_cycle = Cycle(**form_data.dict())

    db.add(new_cycle)
    db.flush()

    for component in form_data.components:

        if component.type == 'product':
            product_type = db.query(Product_Type).filter_by(
                code=component.name, disabled=False).first()

            if not product_type:

                check_product_type = db.query(Product_Type).filter_by(name=component.name, disabled=False).first()

                if check_product_type:
                    raise HTTPException(
                        status_code=400, detail="Ushbu nom band qilingan!")

                product_type = Product_Type(name=component.name)
                db.add(product_type)
                db.flush()

            new_component = Component(
                material_type_id=0,
                product_type_id=product_type.id,
                cycle_id=new_cycle.id,
            )

        else:
            material_type = db.query(Material_Type).filter_by(
                name=component.name, hidden=False).first()
            if not material_type:

                material_type = Material_Type(name=component.name)
                db.add(material_type)
                db.flush()

            new_component = Component(
                material_type_id=material_type.id,
                product_type_id=0,
                cycle_id=new_cycle.id,
            )

        db.add(new_component)
        db.flush()

    db.commit()

    raise HTTPException(status_code=200, detail="Ma`lumotlar saqlandi!")


def update_cycle(id, form_data, usr, db: Session):
    cycle = db.query(Cycle).filter(Cycle.id == id)
    this_cycle = cycle.first()
    if this_cycle:

        unique_name = db.query(Cycle).filter_by(name=form_data.name).filter(
            Cycle.name != this_cycle.name, Cycle.disabled == False, Cycle.product_type_id == this_cycle.product_type_id).first()

        if unique_name:
            raise HTTPException(status_code=400, detail="Bu nom band!")

        cycle.update({
            Cycle.name: form_data.name,
            Cycle.kpi: form_data.kpi,
            Cycle.plan_value: form_data.plan_value,
            Cycle.plan_day: form_data.plan_day,
            Cycle.spending_minut: form_data.spending_minut,
            Cycle.disabled: form_data.disabled,
            Cycle.special: form_data.special,
            Cycle.hasPeriod: form_data.hasPeriod,
        })

        # if form_data.disabled == True:
        #     db.query(Cycle).filter_by(product_type_id=this_cycle.product_type_id, disabled=False)\
        #         .filter(Cycle.ordinate > this_cycle.ordinate).update({
        #             Cycle.ordinate: Cycle.ordinate - 1
        #         })

        # db.query(Component)\
        #     .join(Component.trade_items)\
        #     .join(Trade_items.trade)\
        #     .join(Trades.order)\
        #     .filter(
        #         Component.disabled == False,
        #         Component_Item.disabled == False,
        #         or_(
        #             Orders.status == 'pre_order',
        #             Orders.status == 'false',
        #         )
        # ).having(func.count(Trade_items.id) == 0).update({Component.disabled: True, Component_Item.disabled: True})

        db.query(Plant_Cycle).filter_by(cycle_id=this_cycle.id).update(
            {Plant_Cycle.disabled: True})

        # next_cycle =
        # db.query(Cycle_Store).

        db.commit()

        raise HTTPException(status_code=200, detail="O`zgarish saqlandi!")
    else:
        raise HTTPException(status_code=400, detail="So`rovda xatolik!")


def update_cycle_posistion(form_data: UpdateCyclePosition, usr, db: Session):

    cycle = db.query(Product_Cycle).filter_by(id=form_data.id)
    this_cycle = cycle.first()

    error_req = HTTPException(status_code=400, detail="So`rovda xatolik!")

    if this_cycle:

        ordinate = deepcopy(this_cycle.ordinate)
        if form_data.direction == 'top':
            next_ordinate = ordinate - 1
        else:
            next_ordinate = ordinate + 1

        next_cycle = db.query(Product_Cycle)\
            .filter_by(product_id=this_cycle.product_id, ordinate=next_ordinate, disabled=False)\
            .first()

        if next_cycle:
            db.query(Cycle).filter_by(id=next_cycle.id).update(
                {Cycle.ordinate: deepcopy(ordinate)})
            cycle.update({Cycle.ordinate: deepcopy(next_ordinate)})
            db.commit()

        else:
            raise error_req

        raise HTTPException(status_code=200, detail="O`zgarish saqlandi!")

    raise HTTPException(status_code=400, detail="So`rovda xatolik!")
