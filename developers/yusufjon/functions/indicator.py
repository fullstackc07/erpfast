from developers.abdusamad.functions.incomes import sum_income
from ..models.norm import Norm
from ..models.production import Production
from ..models.plant import Plant
from ..models.product import Product
from ..models.plant_user import *
from ..models.cycle_store import *
from ..models.material_store import *
from ..models.component_item import *
from ..models.plant_cycle import *
from ..models.supply import *
from ..models.production import *
from ..models.plan import *
from ..models.product_cycle import *
from ..models.salary import *
from ..models.production_tree import *
from ..models.attandance import *

from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from datetime import datetime
from datetime import date
from developers.abdusamad.models import *


def get_norms_indicators(usr, db: Session):
    norms = db.query(Norm).options(joinedload(Norm.plant).subqueryload(Plant.plant_users.and_(Plant_User.disabled == False)).subqueryload(
        Plant_User.user).load_only(User.name), joinedload(Norm.olchov)).filter(Norm.disabled == False)

    if usr.role == 'plant_admin':
        norms = norms.filter(Norm.plant_id.in_(
            [one.id for one in usr.plant_users]))

    res = []
    for norm in norms.all():
        ids = norm.products.split(";")
        idss = []
        text = ""
        for x in ids:
            try:
                idss.append(int(x))
                product = db.query(Product).filter_by(id=x).first()
                if product:
                    text += f"{product.name}, "
            except Exception as e:
                pass
        norm.products = text
        norm.done_value = db.query(func.coalesce(func.sum(Production.value), 0)).filter(
            Production.product_id.in_(idss),
            Production.plant_id == norm.plant_id,
            func.date(Production.created_at) >= datetime.now().strftime(
                "%Y-%m-01")
        ).scalar()

        res.append(norm)

    return res


def get_orders_table_func(usr, db: Session):
    orders = db.query(Orders).filter(Orders.status == 'pre_order').order_by(
        Orders.delivery_date.asc()).all()
    res = []

    for ord in orders:
        sum_trade_percent_cycle = 0
        sum_trade_percent_ready = 0

        trade_items = db.query(Trade_items, func.coalesce(func.sum(Trade_items.quantity), 0).label(
            "sum_value")).join(Trade_items.trade).filter(Trades.order_id == ord.id)

        for trd_item in trade_items.group_by(Trade_items.id).all():

            trd_item = trd_item.Trade_items

            if trd_item.component_item.product_id > 0:

                cycle_stores = db.query(func.coalesce(func.sum(Cycle_Store.value), 0))\
                    .join(Cycle_Store.cycle)\
                    .filter(Cycle.product_type_id == trd_item.component_item.product.product_type_id, Cycle_Store.trade_item_id == trd_item.id, Cycle_Store.value > 0)\
                    .scalar()

                if trd_item.quantity < cycle_stores:
                    cycle_percent = trd_item.quantity
                else:
                    cycle_percent = cycle_stores

                product_stores = db.query(func.coalesce(func.sum(Product_Store.value), 0))\
                    .filter(Product_Store.product_id == trd_item.component_item.product_id, Product_Store.trade_item_id == trd_item.id, Product_Store.value > 0)\
                    .scalar()

                if trd_item.quantity < product_stores:
                    ready_percent = trd_item.quantity
                else:
                    ready_percent = product_stores

            elif trd_item.component_item.material_id > 0:
                material_stores = db.query(func.coalesce(func.sum(Material_Store.value), 0))\
                    .filter(Material_Store.material_id == trd_item.component_item.material_id, Material_Store.value > 0)\
                    .scalar()

                if trd_item.quantity < material_stores:
                    ready_percent = trd_item.quantity
                else:
                    ready_percent = material_stores

                cycle_percent = trd_item.quantity

            sum_trade_percent_cycle += cycle_percent
            sum_trade_percent_ready += ready_percent

        trade_items = trade_items.first()
        if trade_items:
            sum_value = trade_items.sum_value
            if sum_value > 0:
                ord.cycle_percent = round(
                    sum_trade_percent_cycle / sum_value * 100)
                ord.ready_percent = round(
                    sum_trade_percent_ready / sum_value * 100)
            else:
                ord.cycle_percent = 100
                ord.ready_percent = 100

        ord.market = ord.market
        ord.customer = ord.customer
        ord.sum_income = sum_income(ord.id, 'order', db)

        res.append(ord)

    return res


def get_trade_item_status(trade_item_id, usr, db: Session):

    trade_item = db.query(Trade_items).filter_by(id=trade_item_id).first()
    if trade_item.component_item.product:
        product = trade_item.component_item.product
        res = []
        cycles = db.query(Cycle).filter_by(
            product_id=product.id, disabled=False).order_by(Cycle.ordinate.asc()).all()
        for cycle in cycles:

            cycle_stores = db.query(Cycle_Store, func.coalesce(func.sum(Cycle_Store.value), 0).label('sum_quantity')).filter_by(cycle_id=cycle.id, trade_item_id=trade_item_id).filter(Cycle_Store.value > 0)\
                .group_by(Cycle_Store.plant_id).all()

            sections = []
            for cy_st in cycle_stores:
                sections.append({'plant_name': cy_st.Cycle_Store.plant.name,
                                'value': cy_st.sum_quantity, 'olchov_name': cy_st.Cycle_Store.olchov.name})

            res.append({
                'cycle': cycle.name,
                'inSections': sections,
            })

        return {
            'cycles': res,
            'ready': db.query(func.coalesce(func.sum(Product_Store.value))).filter_by(product_id=product.id, trade_item_id=trade_item_id).filter(Product_Store.value > 0).scalar(),
            'product_name': product.name,
            'olchov_name': product.olchov.name,
        }


def get_indicators_index(from_date, to_date, usr, db: Session):

    sum_expense = db.query(func.coalesce(func.sum(Expenses.money), 0)).filter(
        func.date(Expenses.time).between(from_date, to_date), Expenses.market_id > 0).scalar()
    sum_income = db.query(func.coalesce(func.sum(Incomes.money), 0)).filter(func.date(
        Expenses.time).between(from_date, to_date), Expenses.market_id > 0).scalar()
    sum_order_discount = db.query(func.coalesce(func.sum(Orders.discount), 0)).filter(
        func.date(Orders.time).between(from_date, to_date), Orders.market_id > 0).scalar()
    orders = db.query(Orders).filter(Orders.market_id > 0).all()
    orders_between_time = db.query(Orders).filter(
        func.date(Orders.time).between(from_date, to_date), Orders.market_id > 0).all()
    sum_returned_price = db.query(func.coalesce(func.sum(Returned_products.quantity * Returned_products.price), 0)).filter(func.date(
        Returned_products.time).between(from_date, to_date), Returned_products.order_id.in_([order.id for order in orders])).scalar()
    sum_trade_discount = db.query(func.coalesce(func.sum(Trades.quantity * Trades.discount), 0)).filter(
        Trades.order_id.in_([order.id for order in orders_between_time])).scalar()
    sum_trade_price = db.query(func.coalesce(func.sum(Trades.quantity * Trades.price), 0)).filter(
        Trades.order_id.in_([order.id for order in orders_between_time])).scalar()
    sum_trade_tan_narx = db.query(func.coalesce(func.sum(Trades.quantity * Product.plant_price), 0) + func.coalesce(func.sum(Trades.quantity * Product_Store.price), 0)).outerjoin(
        (Product, Product.id == Trades.product_id), (Product_Store, Product_Store.id == Trades.product_store_id)).filter(Trades.order_id.in_([order.id for order in orders_between_time])).scalar()
    kassa_balance = db.query(func.coalesce(func.sum(Kassa.balance))).scalar()

    sum_needy_material_for_orders = db.query(func.coalesce(func.sum(Plan.rest_value*Component_Item.value*Material.price), 0))\
        .select_from(Plan)\
        .join(Plan.product).join(Product.product_cycles)\
        .join(Product_Cycle.cycle).join(Cycle.components)\
        .join(Component.component_items).join(Cycle.components).join(Plan.material)\
        .filter(
            Plan.disabled == False,
            Product.disabled == False,
            Product_Cycle.disabled == False,
            Cycle.disabled == False,
            Component.disabled == False,
            Component_Item.disabled == False,
            Component_Item.material_id == Plan.material_id,
            Plan.rest_value > 0,
            Plan.material_id > 0,
            Plan.trade_id > 0
    ).scalar()

    material_store_sub = db.query(func.coalesce(func.sum(Material_Store.value), 0)).filter_by(
        material_id=Material.id
    ).subquery()

    sum_needy_material_for_plant = db.query(func.coalesce(func.sum((Material.alarm_value-material_store_sub)*Material.price), 0)).filter(
        Material.disabled == False, Material.alarm_value > material_store_sub).scalar()

    came_employees_count = db.query(User).join(User.attandances).filter(
        func.date(Attandance.datetime) == date.today(),
        Attandance.type == 'entry'
    ).group_by(User.id).count()

    avanse = db.query(func.coalesce(func.sum(Expenses.money), 0)).filter(
        Expenses.type == 'user_salary',
        Expenses.source > 0,
        Expenses.salary_id > 0
    ).scalar()

    calculated_salary = float(db.query(func.coalesce(func.sum(
        Salary.additional_wage+Salary.calculated_wage-Salary.tax), 0)).scalar()) - avanse


    return {
        "supply": db.query(func.coalesce(func.sum(Supply.value*Supply.price), 0)).filter(
            func.date(Supply.created_at) >= from_date,
            func.date(Supply.created_at) <= to_date,
            Supply.disabled == False
        ).scalar(),
        "production": db.query(func.coalesce(func.sum(Production.value*Production.cost), 0)).filter(
            func.date(Production.created_at) >= from_date,
            func.date(Production.created_at) <= to_date,
            Production.finished == True,
        ).scalar(),

        "sum_expense": sum_expense,
        "calculated_salary": calculated_salary,
        "sum_income": sum_income,
        "sum_discount": sum_order_discount + sum_trade_discount,
        "sum_returned_price": sum_returned_price,
        "sum_trade_price": sum_trade_price,
        "sum_trade_tan_narx": sum_trade_tan_narx,
        "warehouse": db.query(func.coalesce(func.sum(Product_Store.value*Product.plant_price), 0)).join(Product_Store.product).filter(Product_Store.value > 0).scalar() + float(db.query(func.coalesce(func.sum(Material_Store.value*Material_Store.price), 0)).filter(Material_Store.value > 0).scalar()) + db.query(func.coalesce(func.sum(Cycle_Store.value*Cycle_Store.price+Cycle.kpi), 0)).join(Cycle_Store.cycle).filter(Cycle_Store.value > 0).scalar(),
        "supplier_loans": abs(db.query(func.coalesce(func.sum(Supplier.balance), 0)).filter(Supplier.balance > 0).scalar()),
        "customer_loans": db.query(func.coalesce(func.sum(Loans.residual), 0)).filter(Loans.status == False).scalar(),
        "kassa_balance": int(kassa_balance),
        "sum_needy_material_for_orders": sum_needy_material_for_orders,
        "sum_needy_material_for_plant": sum_needy_material_for_plant,
        "came_employees_count": came_employees_count,
    }


def get_orders_status_table(plant_ids: str, usr, db: Session):
    ids = plant_ids.split(";")
    plant_id_all = []
    for x in ids:
        try:
            plant_id_all.append(int(x))
        except Exception as e:
            pass

    orders = db.query(Orders).join(Orders.trades).join(Trades.trade_items).filter(Orders.status == 'pre_order', Trade_items.id > 0).order_by(
        Orders.delivery_date.asc()).all()

    res = []
    for ord in orders:
        orders_by_plants = []
        for plant_id in plant_id_all:
            plant = db.query(Plant).get(plant_id)
            if plant:

                percentage = db.query(func.coalesce(func.avg((Plan.value-Plan.rest_value) / Plan.value * 100), -1))\
                    .select_from(Plan)\
                    .join(Plan.product)\
                    .join(Product.product_cycles)\
                    .join(Product_Cycle.cycle)\
                    .join(Cycle.plant_cycles)\
                    .filter(
                    Plan.order_id == ord.id,
                    Cycle.disabled == False,
                    Plant_Cycle.disabled == False,
                    Plant_Cycle.plant_id == plant_id,
                )\
                    .scalar()

                orders_by_plants.append({
                    'order_id': ord.id,
                    'delivery_date': ord.delivery_date,
                    'plant': plant.name,
                    'percentage': percentage,
                })
        res.append({"row": orders_by_plants})

    return res
