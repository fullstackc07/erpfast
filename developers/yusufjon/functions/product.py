import math
import time
from sqlalchemy import or_
from sqlalchemy.orm import joinedload, Session, subqueryload
from fastapi import HTTPException
from developers.yusufjon.models.component import Component
from developers.yusufjon.models.component_item import Component_Item
from developers.yusufjon.models.cycle import Cycle
from developers.yusufjon.models.user_kpi import User_Kpi
from developers.yusufjon.models.user import User
from developers.yusufjon.models.product import *
from developers.yusufjon.models.production_tree import *
from developers.yusufjon.utils.trlatin import tarjima
from ..models.product_cycle import *




def get_all_products(disabled, product_type_id, search, page, limit, usr, db: Session):

    if page == 1 or page < 1:
        offset = 0
    else:
        offset = (page-1) * limit

    products = db.query(Product).options(
        joinedload(Product.olchov),
        joinedload(Product.product_type)
    ).filter_by(disabled=disabled, product_type_id=product_type_id)

    if search:
        products = products.filter(
            or_(
                Product.name.like(f"%{tarjima(search, 'uz')}%"),
                Product.name.like(f"%{tarjima(search, 'ru')}%"),
            )
        )

    all_data = products.order_by(Product.name.asc()).offset(offset).limit(limit)
    count_data = products.count()

    return {
        "data": all_data.all(),
        "page_count": math.ceil(count_data / limit),
        "data_count": count_data,
        "current_page": page,
        "page_limit": limit,
    }


def get_one_product(product_id, db: Session):

    product = db.query(Product).options(
        joinedload(Product.olchov),
        joinedload(Product.product_type),
        joinedload(Product.product_cycles.and_(Product_Cycle.disabled==False)).options(
            joinedload(Product_Cycle.cycle).options(
                subqueryload(Cycle.components.and_(Component.disabled == False)).options(
                    subqueryload(Component.product_type),
                    subqueryload(Component.material_type),
                ),
                subqueryload(Cycle.user_kpis.and_(User_Kpi.disabled == False)).options(
                    subqueryload(User_Kpi.user).load_only(User.name),
                ),
            )
        )
    ).filter_by(id=product_id).first()

    if not product:
        raise HTTPException(status_code=400, detail="Mahsulot topilmadi")

    return product

def get_one_product_type(product_type_id, db: Session):

    product = db.query(Product_Type).options(
        joinedload(Product_Type.olchov),
        joinedload(Product_Type.cycles.and_(Cycle.disabled == False)).options(
          
            subqueryload(Cycle.user_kpis.and_(User_Kpi.disabled == False)).options(
                subqueryload(User_Kpi.user).load_only(User.name),
            ),
        )
    ).get(product_type_id)

    if not product:
        raise HTTPException(status_code=400, detail="Mahsulot topilmadi")

    return product


def make_tree(for_product_id, product, db: Session, value=1):
    res = []
    product_cycles = db.query(Product_Cycle).filter_by(product_id=product.id, disabled=False).order_by(Product_Cycle.ordinate.desc()).all()
    for product_cycle in product_cycles:
        cycle = product_cycle.cycle
        plant_cycles = cycle.plant_cycles
        for plant_cycle in plant_cycles:
            if plant_cycle.disabled == False:

                res_item = {
                    "product_id":product.id,
                    "for_product_id":for_product_id,
                    "plant_id":plant_cycle.plant_id,
                    "plant":plant_cycle.plant.name,
                    "cycle_ordinate":product_cycle.ordinate,
                    "cycle_id":cycle.id,
                    "value":value,
                }

                res.append(res_item)


        # Move the second loop outside of the first loop
    components = [component for product_cycle in product_cycles for component in product_cycle.cycle.components if not component.disabled]


    for component in components:
        component_items = component.component_items
        for component_item in component_items:
            if component_item.disabled == False and component_item.product_id > 0:
                product2 = db.query(Product).get(component_item.product_id)
                for item in make_tree(for_product_id, product2, db, (value*component_item.value)):
                    res.append(item)
   
    return res




def create_tree(product, usr, db):
    db.query(Production_Tree).filter(
            Production_Tree.for_product_id == product.id).delete()
    db.commit()

    datas = make_tree(product.id, product, db)

    for item in datas:

        last_ordinate = db.query(Production_Tree)\
            .filter_by(for_product_id=product.id).order_by(Production_Tree.ordinate.desc())\
            .first()

        last_ordinate_same = db.query(Production_Tree)\
            .filter_by(for_product_id=product.id, product_id=item['product_id'], cycle_id=item['cycle_id'], value=item['value'])\
            .first()

        if last_ordinate_same:
            ordinate = last_ordinate_same.ordinate
        else:
            ordinate = last_ordinate.ordinate+1 if last_ordinate else 1

        new_pr_tree = Production_Tree(
            product_id=item['product_id'],
            for_product_id=product.id,
            plant_id=item['plant_id'],
            value=item['value'],
            cycle_id=item['cycle_id'],
            ordinate=ordinate,
        )

        db.add(new_pr_tree)
        db.commit()

    return datas
    # if len(num_cyc) > 0:
    raise HTTPException(status_code=200, detail="Ma`lumotlar saqlandi!")