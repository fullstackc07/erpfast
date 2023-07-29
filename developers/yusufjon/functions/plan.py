from developers.yusufjon.models.cycle_store import *
from developers.yusufjon.models.plan import *
from developers.yusufjon.models.component import *
from developers.yusufjon.models.production_tree import *
from developers.yusufjon.models.material_store import *
from developers.yusufjon.models.product_cycle import *
from datetime import timedelta
import math
import datetime
from sqlalchemy import Interval, bindparam, or_, func, text
from sqlalchemy.orm import joinedload, Session
from sqlalchemy.sql import label
from fastapi import HTTPException
from developers.abdusamad.models import *
from ..utils.trlatin import tarjima


def get_all_plans(product_id, search, disabled, page, limit, usr, db: Session):
    if page == 1 or page < 1:
        offset = 0
    else:
        offset = (page-1) * limit

    plans = db.query(Plan).options(
        joinedload(Plan.product).subqueryload(Product.olchov))\
        .options(joinedload(Plan.product).subqueryload(Product.product_type)).filter(Plan.disabled == disabled, Plan.rest_value > 0)

    if product_id > 0:
        plans = plans.filter(Plan.product_id==product_id)

    if len(search) > 0:
        plans = plans.join(Plan.product).filter(
            or_(
                Product.name.like(f"%{search}%"),
                Plan.comment.like(f"%{search}%"),
                Plan.value.like(f"%{search}%"),
            )
        )

    all_data = plans.order_by(Plan.id.desc()).offset(offset).limit(limit)
    count_data = plans.count()

    return {
        "data": all_data.all(),
        "page_count": math.ceil(count_data / limit),
        "data_count": count_data,
        "current_page": page,
        "page_limit": limit,
    }

def get_plan_products(search: str, page, limit, product_type_id: int, usr: User, db: Session):

    if page == 1 or page < 1:
        offset = 0
    else:
        offset = (page-1) * limit

    cycle_store = db.query(func.coalesce(func.sum(Cycle_Store.value), 0)).filter(
        Cycle_Store.product_id==Product.id
    ).subquery()

    # raise HTTPException(status_code=400, detail=f"id:{product_type_id}")

    products = db.query(
        label("id", Product.id),
        label("name", Product.name),
        label("image", Product.image),
        label("olchov", Olchov.name),
        label("plan_value", func.coalesce(func.sum(Plan.value))),
        label("rest_value", func.coalesce(func.sum(Plan.rest_value))),
        label("cycle_value", cycle_store),
    ).select_from(Product).join(Product.olchov).join(Product.plans).filter(
        Product.product_type_id==product_type_id,
    )

    if len(search) > 0:
        products = products.filter(
            or_(
                Product.name.like(f"%{tarjima(search, 'ru')}%"),
                Product.name.like(f"%{tarjima(search, 'uz')}%"),
            )
        )

    products = products.group_by(Product.id)

    all_data = products.order_by(Product.name.asc()).offset(offset).limit(limit)
    count_data = products.count()

    return {
        "data": all_data.all(),
        "page_count": math.ceil(count_data / limit),
        "data_count": count_data,
        "current_page": page,
        "page_limit": limit,
    }


def create_new_plan(form_data, usr, db: Session):

    new_plan = Plan(
        product_id=form_data.product_id,
        value=form_data.value,
        comment=form_data.comment,
        rest_value=form_data.value,
        size1=form_data.size1,
        size2=form_data.size2,
        user_id=usr.id,
        material_id=form_data.material_id,
        to_date=form_data.to_date,
        disabled=form_data.disabled
    )

    trees = db.query(Production_Tree).filter(Production_Tree.for_product_id==form_data.product_id).count()

    if trees==0:
        raise HTTPException(status_code=400, detail="Mahsulotga jarayon biriktiring va yangilang!")

    create_plans_for_order(new_plan, usr, db, True)

    raise HTTPException(status_code=200, detail="Ma`lumotlar saqlandi!")



def update_plan(id, form_data, usr, db: Session):
    plans = db.query(Plan).filter(Plan.id == id)
    this_plan = plans.first()

    if this_plan:

        product = db.query(Product).get(form_data.product_id)

        if not product:
            raise HTTPException(status_code=400, detail="Mahsulot topilmadi")

        rest_value = form_data.value - (this_plan.value-this_plan.rest_value)

        if rest_value < 0:
            rest_value = 0
            form_data.disabled=False


        plans.update({
            Plan.product_id: form_data.product_id,
            Plan.value: form_data.value,
            Plan.rest_value: rest_value,
            Plan.material_id: form_data.material_id,
            Plan.comment: form_data.comment,
            Plan.size1: form_data.size1,
            Plan.size2: form_data.size2,
            Plan.to_date: form_data.to_date,
            Plan.disabled: form_data.disabled
        })

        db.commit()

        raise HTTPException(status_code=200, detail="Ma`lumotlar saqlandi!")
    else:
        raise HTTPException(status_code=400, detail="So`rovda xatolik!")
    


def create_plans_for_order(that_plan, usr, db, forPlant: bool = False):


    if that_plan.product_id > 0:

        sequence = 1

        needy_value = that_plan.value

        product_trees_by_product = db.query(Production_Tree.product_id, Production_Tree.value)\
            .filter_by(for_product_id=that_plan.product_id)\
            .order_by(Production_Tree.ordinate.asc())\
            .group_by(Production_Tree.product_id, Production_Tree.value).all()

        # boladigan barcha jarayonlar
        for product_tree in product_trees_by_product:
            if needy_value > 0:
                if sequence > 1:

                    if that_plan.size1 == 0:
                        size1_b = 1

                    if that_plan.size2 == 0:
                        size2_b = 1

                    needy_value_2 = product_tree.value * needy_value * size1_b * size2_b
                else:
                    needy_value_2 = product_tree.value * needy_value

                # agar size lar keraksiz joyda bolsa
                if sequence > 1:
                    that_plan.size1 = 0
                    that_plan.size2 = 0

                product_store_sum = db.query(func.coalesce(func.sum(Product_Store.value), 0))\
                    .filter(Product_Store.value > 0)\
                    .filter_by(
                    product_id=product_tree.product_id,
                    trade_id=0, trade_item_id=0, market_id=0,
                    size1=that_plan.size1, size2=that_plan.size2, material_id=that_plan.material_id
                ).scalar()

                cycle_store_sum = db.query(func.coalesce(func.sum(Cycle_Store.value), 0))\
                    .filter(Cycle_Store.value > 0)\
                    .filter_by(
                    product_id=product_tree.product_id,
                    trade_id=0, trade_item_id=0,
                    size1=that_plan.size1, size2=that_plan.size2, material_id=that_plan.material_id
                ).scalar()

                plan_bron_value = db.query(func.coalesce(func.sum(Plan.bron_value), 0))\
                    .join(Orders, Plan.order_id == Orders.id)\
                    .filter(Orders.status == 'pre_order', Plan.product_id == product_tree.product_id, Plan.material_id == that_plan.material_id)\
                    .scalar()

                absolute_free_store = product_store_sum + cycle_store_sum - plan_bron_value
                plan_bron = (absolute_free_store if absolute_free_store <=
                             needy_value_2 else needy_value_2)
                total_plan_value = needy_value_2 - plan_bron

                if forPlant == True and product_tree.product_id == that_plan.product_id:
                    total_plan_value = needy_value_2

                if sequence == 1:
                    product_stores = db.query(Product_Store).filter_by(
                        product_id=that_plan.product_id,
                        trade_id=0,
                        trade_item_id=0,
                        market_id=0,
                        size1=that_plan.size1,
                        size2=that_plan.size2,
                        material_id=that_plan.material_id
                    ).filter(Product_Store.value > 0).all()

                    for pr_store in product_stores:
                        if needy_value > 0:
                            if pr_store.value <= needy_value:
                                needy_value -= pr_store.value

                                if that_plan.trade_item_id:
                                    trade_item_price = that_plan.trade_item.price
                                else:
                                    trade_item_price = 0
                                    

                                db.query(Product_Store).filter_by(id=pr_store.id).update(
                                    {Product_Store.trade_id: that_plan.trade_id, Product_Store.trade_item_id: that_plan.trade_item_id, Product_Store.price: trade_item_price})
                            else:
                                db.query(Product_Store).filter_by(id=pr_store.id).update(
                                    {Product_Store.value: Product_Store.value - needy_value})
                                db.add(Product_Store(
                                    product_id=pr_store.product_id,
                                    value=needy_value,
                                    price=pr_store.price,
                                    trade_price=pr_store.trade_price,
                                    trade_id=pr_store.trade_id,
                                    trade_item_id=that_plan.trade_item_id,
                                    size1=that_plan.size1,
                                    size2=that_plan.size2,
                                    material_id=that_plan.material_id
                                ))
                                needy_value = 0
                        else:
                            break

                # if trade_item.material_id > 0:

                #     compomenents = db.query(Component).filter(
                #         Component.material_type_id == trade_item.material.material_type_id,
                #         Component.disabled == False
                #     ).all()

                #     total_needy_material_value = 0

                #     for com in compomenents:
                #         total_needy_material_value += com.value

                #     total_needy_material_value = math.ceil(
                #         total_needy_material_value * total_plan_value * 10000) / 10000,

                    # material_store = db.query(func.coalesce(func.sum(Material_Store.value))).filter_by(
                    #     material_id=trade_item.material_id).scalar()

                    # bron_material_value = db.query(func.coalesce(
                    #     func.sum(Component.value*Plan.rest_value)
                    # )).select_from(Plan)\
                    #     .join(Plan.product)\
                    #     .join(Plan.order)\
                    #     .join(Product.product_cycles)\
                    #     .join(Product_Cycle.cycle)\
                    #     .join(Cycle.components)\
                    #     .join(Component.component_items)\
                    #     .filter(
                    #         Component.disabled == False,
                    #         Component_Item.disabled == False,
                    #         Component_Item.material_id == trade_item.material_id,
                    #         Product_Cycle.disabled == False,
                    #         Orders.status == 'pre_order',
                    # ).scalar()
                
                new_plan = Plan(
                    product_id=product_tree.product_id,
                    order_id=that_plan.order_id,
                    trade_id=that_plan.trade_id,
                    trade_item_id=that_plan.trade_item_id,
                    size1=that_plan.size1,
                    size2=that_plan.size2,
                    comment=that_plan.comment,
                    value=math.ceil(total_plan_value * 10000) / 10000,
                    bron_value=math.ceil(plan_bron * 10000) / 10000,
                    rest_value=math.ceil(total_plan_value * 10000) / 10000,
                    user_id=usr.id,
                    material_id=that_plan.material_id,
                    from_date=func.now(),
                    to_date=that_plan.to_date,
                    disabled=False,
                    product_type_id=db.query(Product).get(
                        product_tree.product_id).product_type_id
                )

                db.add(new_plan)
                db.commit()

                needy_value = total_plan_value
                sequence += 1
