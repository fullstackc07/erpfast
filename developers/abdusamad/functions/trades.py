from fastapi import HTTPException

from developers.yusufjon.functions.plan import create_plans_for_order
from ..models import Trades, Trade_items, Trade_items_size, Orders, Returned_products, Kassa, Expenses
from ...yusufjon.models.product_store import Product_Store
from ...yusufjon.models.product import Product
from ...yusufjon.models.component_item import Component_Item
from ...yusufjon.models.material import Material
from ...yusufjon.models.cycle_store import Cycle_Store
from ...yusufjon.models.product_store import Product_Store
from ...yusufjon.models.material_store import Material_Store
from ...yusufjon.models.product_type import Product_Type
from ...yusufjon.models.production_tree import *
from ...yusufjon.models.plan import *
from sqlalchemy import func
from sqlalchemy.orm import joinedload, Session
import math
from datetime import datetime


def all_trades(order_id, related_number, page, limit, db):
    if order_id:
        order_filter = Trades.order_id == order_id
    else:
        order_filter = Trades.order_id > 0
    if related_number:
        trades = db.query(Trades, func.coalesce(func.sum(Trades.quantity), 0).label("sum_quantity")).options(joinedload(Trades.product_store).subqueryload(Product_Store.product).options(joinedload(Product.product_type), joinedload(Product.olchov)), joinedload(Trades.order), joinedload(Trades.user), joinedload(Trades.product).options(joinedload(Product.product_type), joinedload(Product.olchov)), joinedload(
            Trades.trade_items).options(joinedload(Trade_items.component_item).options(joinedload(Component_Item.material).options(joinedload(Material.olchov), joinedload(Material.material_type)), joinedload(Component_Item.product).options(joinedload(Product.olchov), joinedload(Product.product_type)), joinedload(Component_Item.component)))).filter(order_filter).group_by(Trades.related_number)
        return {"current_page": page, "limit": limit, "pages": math.ceil(trades.count() / limit), "data": trades.offset((page - 1) * limit).limit(limit).all()}
    else:
        data2 = []
        trades = db.query(Trades, func.coalesce(func.sum(Trades.quantity), 0).label("sum_quantity")).options(joinedload(Trades.product_store).subqueryload(Product_Store.product).options(joinedload(Product.product_type), joinedload(Product.olchov)), joinedload(Trades.order), joinedload(Trades.user), joinedload(Trades.product).options(joinedload(Product.product_type), joinedload(Product.olchov)), joinedload(
            Trades.trade_items).options(joinedload(Trade_items.component_item).options(joinedload(Component_Item.material).options(joinedload(Material.olchov), joinedload(Material.material_type)), joinedload(Component_Item.product).options(joinedload(Product.olchov), joinedload(Product.product_type)), joinedload(Component_Item.component)))).filter(order_filter).group_by(Trades.id)
        for trade in trades:
            trade_item_sum_price = db.query(func.sum(
                Trade_items.quantity * Trade_items.price)).filter(Trade_items.trade_id == trade.Trades.id).scalar()
            data2.append({"trade_id": trade.Trades.id,
                         "sum_price": trade_item_sum_price})
        return {"current_page": page, "limit": limit, "pages": math.ceil(trades.count() / limit), "data": trades.offset((page - 1) * limit).limit(limit).all(), "data2": data2}


def all_trade_items(trade_id, db):
    trades = db.query(Trade_items).options(
        joinedload(Trade_items.component_item).options(joinedload(Component_Item.material).options(joinedload(Material.olchov), joinedload(Material.material_type)),
                                                       joinedload(Component_Item.product).options(joinedload(Product.olchov), joinedload(Product.product_type)), joinedload(Component_Item.component)),
        joinedload(Trade_items.user),
        joinedload(Trade_items.material),
        joinedload(Trade_items.trade)
    ).filter(Trade_items.trade_id == trade_id)
    return trades.all()


def one_trade(id, order_id, db):
    if order_id:
        order = db.query(Orders).filter(Orders.id == order_id).first()
        if order.status == "pre_order":
            return db.query(func.coalesce(func.sum(Trade_items.price * Trade_items.quantity), 0)).filter(Trade_items.trade_id.in_([trade.id for trade in db.query(Trades).filter(Trades.order_id == order_id).all()])).scalar()
        elif order.status == "false":
            return db.query(func.coalesce(func.sum(Trades.quantity * (Trades.price - Trades.discount)), 0)).filter(Trades.order_id == order_id).scalar()
        if order.status == "true" and order.delivery_date != "0000-00-00":
            return db.query(func.coalesce(func.sum(Trade_items.price * Trade_items.quantity), 0)).filter(Trade_items.trade_id.in_([trade.id for trade in db.query(Trades).filter(Trades.order_id == order_id).all()])).scalar()
        elif order.status == "true" and order.delivery_date == "0000-00-00":
            return db.query(func.coalesce(func.sum(Trades.quantity * (Trades.price - Trades.discount)), 0)).filter(Trades.order_id == order_id).scalar()
    return db.query(Trades, func.sum(Trades.quantity).label("sum_quantity")).options(joinedload(Trades.product_store).subqueryload(Product_Store.product).options(joinedload(Product.product_type), joinedload(Product.olchov)), joinedload(Trades.order), joinedload(Trades.user)).group_by(Trades.related_number).filter(Trades.id == id).first()


def returned_products(order_id, market_id, page, limit, db):
    if order_id:
        order_filter = Returned_products.order_id == order_id
    else:
        orders = db.query(Orders).filter(Orders.market_id == market_id).all()
        order_filter = Returned_products.order_id.in_(
            [order.id for order in orders])
    data = db.query(Returned_products, func.sum(Returned_products.quantity).label("sum_quantity")).options(joinedload(Returned_products.trade).subqueryload(Trades.product_store).subqueryload(
        Product_Store.product).options(joinedload(Product.product_type).subqueryload(Product_Type.olchov), joinedload(Product.olchov))).group_by(Returned_products.related_number).filter(order_filter)
    return {"current_page": page, "limit": limit, "pages": math.ceil(data.count() / limit), "data": data.offset((page - 1) * limit).limit(limit).all()}


def trade_status(order_id, db):
    data = []
    for trade in db.query(Trades).filter(Trades.order_id == order_id).all():
        trade_items = db.query(Trade_items).filter(
            Trade_items.trade_id == trade.id).all()
        for trade_item in trade_items:
            comp_item = db.query(Component_Item).filter(
                Component_Item.id == trade_item.component_item_id).first()
            sum_cycle_store = db.query(func.coalesce(func.sum(Cycle_Store.value), 0)).filter(
                Cycle_Store.trade_id == trade.id, Cycle_Store.trade_item_id == trade_item.id).scalar()
            sum_product_store = 0
            sum_material_store = 0
            if comp_item.product_id and comp_item.product_id > 0:
                sum_product_store = db.query(func.coalesce(func.sum(Product_Store.value), 0)).filter(
                    Product_Store.trade_id == trade.id, Product_Store.product_id == comp_item.product_id, Product_Store.trade_item_id == trade_item.id).scalar()
            elif comp_item.material_id and comp_item.material_id > 0:
                sum_material_store = db.query(func.coalesce(func.sum(Material_Store.value), 0)).filter(
                    Material_Store.material_id == comp_item.material_id, Material_Store.plant_id == 0).scalar()
            data.append({"trade_id": trade.id, "trade_item_id": trade_item.id, "sum_product_store": sum_product_store,
                        "sum_material_store": sum_material_store, "sum_cycle_store": sum_cycle_store})
    return data


def sell_product(form, user, db):
    product_sum_quantity = db.query(func.sum(Product_Store.value)).filter(Product_Store.product_id == form.product_store_pr_id, Product_Store.material_id == form.material_id, Product_Store.market_id ==
                                                                          user.market_id, Product_Store.size1 == form.size1, Product_Store.size2 == form.size2).group_by(Product_Store.product_id).scalar()
    if product_sum_quantity is None or product_sum_quantity < form.quantity:
        raise HTTPException(
            status_code=400, detail="Kiritilayotgan hajmda xatolik")
    products = db.query(Product_Store).filter(Product_Store.product_id == form.product_store_pr_id, Product_Store.material_id == form.material_id, Product_Store.market_id ==
                                              user.market_id, Product_Store.size1 == form.size1, Product_Store.size2 == form.size2).all()
    trade_quantity = form.quantity
    order_ver = db.query(Orders).filter(Orders.id == form.order_id).first()
    if order_ver is None or order_ver.status != "false" or order_ver.market_id != user.market_id:
        raise HTTPException(
            status_code=400, detail="Bunday buyurtma mavjud emas yoki yakunlangan")
    trade_related_number_verification = db.query(
        Trades).order_by(Trades.related_number.desc()).first()
    trade_ver = db.query(Trades).join(Product_Store).options(joinedload(Trades.product_store)).filter(Product_Store.product_id ==
                                                                                                      form.product_store_pr_id, Product_Store.size1 == form.size1, Product_Store.size2 == form.size2, Trades.order_id == form.order_id).first()
    if trade_ver:
        raise HTTPException(
            status_code=400, detail="Bunday mahsulotlar sotilganlar ro'yhatida mavjud")
    if trade_related_number_verification:
        related_number = trade_related_number_verification.related_number + 1
    else:
        related_number = 1
    for product in products:
        if product.value >= trade_quantity:
            db.query(Product_Store).filter(Product_Store.id == product.id).update({
                Product_Store.value: Product_Store.value - trade_quantity
            })
            new_trade_db = Trades(
                product_store_id=product.id,
                quantity=trade_quantity,
                price=form.price,
                discount=form.discount,
                related_number=related_number,
                order_id=form.order_id,
                user_id=user.id
            )
            db.add(new_trade_db)
            db.commit()
            db.refresh(new_trade_db)
            trade_quantity = 0
        elif product.value < trade_quantity and product.value > 0:
            trade_verification = db.query(Trades).filter(
                Trades.product_store_id == product.id, Trades.order_id == form.order_id).first()
            if trade_verification:
                db.query(Trades).filter(Trades.id == trade_verification.id).update({
                    Trades.value: Trades.value + product.value
                })
            else:
                new_trade_db = Trades(
                    product_store_id=product.id,
                    quantity=product.value,
                    price=form.price,
                    discount=form.discount,
                    related_number=related_number,
                    order_id=form.order_id,
                    user_id=user.id
                )
                db.add(new_trade_db)
                db.refresh(new_trade_db)
            db.query(Product_Store).filter(Product_Store.id == product.id).update({
                Product_Store.value: 0
            })
            db.commit()
            trade_quantity -= product.value


def delete_trade(id, db, user):
    if one_trade(id, 0, db).Trades is None:
        raise HTTPException(
            status_code=400, detail="Bunday id raqamli savdo mavjud emas")
    order_ver = db.query(Orders).filter(Orders.id == one_trade(
        id, 0, db).Trades.order_id, Orders.market_id == user.market_id).first()
    if order_ver is None or order_ver.status != "false":
        raise HTTPException(
            status_code=400, detail="Ushbu buyurtma yakunlangan")
    for trade in db.query(Trades).filter(Trades.related_number == one_trade(id, 0, db).Trades.related_number).all():
        db.query(Product_Store).filter(Product_Store.id == trade.product_store_id).update({
            Product_Store.value: Product_Store.value + trade.quantity
        })
        db.delete(trade)
        db.commit()


def return_product(form, db, user):
    trade_ver = db.query(Trades).filter(Trades.id == form.trade_id).first()
    if trade_ver is None:
        raise HTTPException(
            status_code=400, detail="Bunday id raqamli savdo mavjud emas")
    order_ver = db.query(Orders).filter(Orders.id == trade_ver.order_id, Orders.market_id ==
                                        user.market_id, Orders.status == "true", Orders.delivery_date == "0000-00-00").first()
    if order_ver is None:
        raise HTTPException(status_code=400, detail="Buyurtmada hatolik")
    trade_sum_quantity = db.query(func.coalesce(func.sum(Trades.quantity), 0)).filter(
        Trades.order_id == trade_ver.order_id, Trades.related_number == trade_ver.related_number).scalar()
    sum_returned_quantity = db.query(func.coalesce(func.sum(Returned_products.quantity))).filter(
        Returned_products.order_id == order_ver.id, Returned_products.related_number == trade_ver.related_number).scalar()
    if form.quantity <= 0 or form.quantity > trade_sum_quantity or sum_returned_quantity and sum_returned_quantity + form.quantity > trade_sum_quantity:
        raise HTTPException(status_code=400, detail="Hajmda hatolik")
    all_trades = db.query(Trades).filter(Trades.order_id == trade_ver.order_id,
                                         Trades.related_number == trade_ver.related_number).all()
    returning_quantity = form.quantity
    kassa_ver = db.query(Kassa).filter(
        Kassa.id == form.kassa_id, Kassa.market_id == user.market_id).first()
    if kassa_ver is None or form.price <= 0 or kassa_ver.balance < form.quantity * form.price:
        raise HTTPException(
            status_code=400, detail="Kassada yetarli mablag' mavjud emas")
    db.query(Kassa).filter(Kassa.id == kassa_ver.id).update({
        Kassa.balance: Kassa.balance - form.quantity * form.price
    })
    db.commit()
    for trade in all_trades:
        if returning_quantity > trade.quantity and trade.quantity > 0:
            returning_quantity -= trade.quantity
            db.query(Product_Store).filter(Product_Store.id == trade.product_store_id).update({
                Product_Store.value: Product_Store.value + trade.quantity
            })
            db.commit()
            new_ret_pr_db = Returned_products(
                trade_id=trade.id,
                related_number=trade.related_number,
                order_id=trade.order_id,
                quantity=trade.quantity,
                price=form.price,
                time=datetime.now().date(),
                user_id=user.id
            )
            db.add(new_ret_pr_db)
            db.commit()
            db.refresh(new_ret_pr_db)
            new_expense_db = Expenses(
                money=trade.quantity * form.price,
                type="returned_product",
                source=new_ret_pr_db.id,
                time=datetime.now().date(),
                comment="",
                kassa_id=kassa_ver.id,
                user_id=user.id,
                market_id=user.market_id
            )
            db.add(new_expense_db)
            db.commit()
            db.refresh(new_expense_db)
        if returning_quantity == trade.quantity and returning_quantity > 0:
            db.query(Product_Store).filter(Product_Store.id == trade.product_store_id).update({
                Product_Store.value: Product_Store.value + trade.quantity
            })
            db.commit()
            returning_quantity = 0
            new_ret_pr_db = Returned_products(
                trade_id=trade.id,
                related_number=trade.related_number,
                order_id=trade.order_id,
                quantity=trade.quantity,
                price=form.price,
                time=datetime.now().date(),
                user_id=user.id
            )
            db.add(new_ret_pr_db)
            db.commit()
            db.refresh(new_ret_pr_db)
            new_expense_db = Expenses(
                money=trade.quantity * form.price,
                type="returned_product",
                source=new_ret_pr_db.id,
                time=datetime.now().date(),
                comment="",
                kassa_id=kassa_ver.id,
                user_id=user.id,
                market_id=user.market_id
            )
            db.add(new_expense_db)
            db.commit()
            db.refresh(new_expense_db)
            raise HTTPException(
                status_code=200, detail="Amaliyot muvaffaqiyatli amalga oshirildi")
        elif returning_quantity <= trade.quantity and returning_quantity > 0:
            db.query(Product_Store).filter(Product_Store.id == trade.product_store_id).update({
                Product_Store.value: Product_Store.value + returning_quantity
            })
            db.commit()
            new_ret_pr_db = Returned_products(
                trade_id=trade.id,
                related_number=trade.related_number,
                order_id=trade.order_id,
                quantity=returning_quantity,
                price=form.price,
                time=datetime.now().date(),
                user_id=user.id
            )
            db.add(new_ret_pr_db)
            db.commit()
            db.refresh(new_ret_pr_db)
            new_expense_db = Expenses(
                money=returning_quantity * form.price,
                type="returned_product",
                source=new_ret_pr_db.id,
                time=datetime.now().date(),
                comment="",
                kassa_id=kassa_ver.id,
                user_id=user.id,
                market_id=user.market_id
            )
            db.add(new_expense_db)
            db.commit()
            db.refresh(new_expense_db)
            returning_quantity = 0
            raise HTTPException(
                status_code=200, detail="Amaliyot muvaffaqiyatli amalga oshirildi")


def take_product_to_pre_order(form, user, db):
    order_ver = db.query(Orders).filter(
        Orders.id == form.order_id, Orders.market_id == user.market_id).first()
    if order_ver is None or order_ver.status != "pre_order":
        raise HTTPException(
            status_code=400, detail="Bunday buyurtma mavjud emas yoki yakunlangan")
    pr_verification = db.query(Product).filter(
        Product.id == form.product_id, Product.disabled == False).first()
    if pr_verification is None:
        raise HTTPException(
            status_code=400, detail="Bunday id raqamli mahsulot mavjud emas")
    trade_ver = db.query(Trades).filter(
        Trades.product_id == form.product_id, Trades.order_id == form.order_id).first()
    if trade_ver:
        raise HTTPException(
            status_code=400, detail="Bunday mahsulot sotilganlar ro'yhatida mavjud")
    new_trade_db = Trades(
        product_id=form.product_id,
        quantity=form.quantity,
        price=form.price,
        discount=0,
        order_id=form.order_id,
        user_id=user.id
    )
    db.add(new_trade_db)
    db.commit()
    db.refresh(new_trade_db)


def delete_product_from_pre_order(id, db, user):
    if one_trade(id, 0, db).Trades is None:
        raise HTTPException(
            status_code=400, detail="Bunday id raqamli savdo mavjud emas")
    order_ver = db.query(Orders).filter(Orders.id == one_trade(
        id, 0, db).Trades.order_id, Orders.market_id == user.market_id).first()
    if order_ver is None or order_ver.status != "pre_order":
        raise HTTPException(
            status_code=400, detail="Ushbu buyurtma yakunlangan")
    pr_store_ver = db.query(Product_Store).filter(
        Product_Store.trade_id == id, Product_Store.value > 0).first()
    if pr_store_ver:
        raise HTTPException(
            status_code=400, detail="Ushbu mahsulot ishlab chiqarilgani sababli o'chirib bo'lmaydi")
    db.delete(one_trade(id, 0, db).Trades)
    db.commit()


def take_component_item_to_pre_order(form, user, db: Session):
    if one_trade(form.trade_id, 0, db).Trades is None or one_trade(form.trade_id, 0, db).Trades.product_id == 0:
        raise HTTPException(
            status_code=400, detail="Bunday id raqamli savdo mavjud emas")
    order_ver = db.query(Orders).filter(Orders.id == one_trade(
        form.trade_id, 0, db).Trades.order_id, Orders.market_id == user.market_id).first()
    if order_ver is None or order_ver.status != "pre_order":
        raise HTTPException(
            status_code=400, detail="Bunday buyurtma mavjud emas yoki yakunlangan")
    if form.size1 and form.size2 == 0 or form.size2 and form.size1 == 0:
        raise HTTPException(status_code=400, detail="Razmerda xatolik")
    component_item_verification = db.query(Component_Item).filter(Component_Item.material_id == form.material_id,
                                                                  Component_Item.product_id == form.product_id, Component_Item.component_id == form.component_id).first()

    if component_item_verification is None:
        new_comp_item_db = Component_Item(
            material_id=form.material_id,
            product_id=form.product_id,
            component_id=form.component_id,
            value=form.quantity
        )
        db.add(new_comp_item_db)
        db.commit()
        db.refresh(new_comp_item_db)
        comp_item_id = new_comp_item_db.id
    else:
        comp_item_id = component_item_verification.id
    trade_item_verification1 = db.query(Trade_items).filter(
        Trade_items.component_item_id == comp_item_id, Trade_items.trade_id == form.trade_id)
    if trade_item_verification1.first():
        for trade_item_verification in trade_item_verification1.all():
            trade_item_size_verification = db.query(Trade_items_size).filter(
                Trade_items_size.trade_item_id == trade_item_verification.id).first()
            if trade_item_size_verification:
                if trade_item_size_verification.size1 == form.size1 and trade_item_size_verification.size2 == form.size2 and trade_item_size_verification.comment == form.comment:
                    raise HTTPException(
                        status_code=400, detail="Bunday mahsulot buyurtmada mavjud")
            else:
                if form.size1 == 0 and form.size2 == 0 and form.comment == "":
                    raise HTTPException(
                        status_code=400, detail="Bunday mahsulot buyurtmada mavjud")
    pr = db.query(Product, Product_Type).outerjoin(Product_Type, Product_Type.id ==
                                                   Product.product_type_id).filter(Product.id == form.product_id).first()
    if pr.Product and pr.Product_Type.hasSize:
        if form.size1 <= 0 or form.size2 <= 0:
            raise HTTPException(
                status_code=400, detail="Razmer biriktirilmagan")
        narx = form.size1 * form.size2 / 10000 * form.price
    else:
        narx = form.price
    new_trade_item_db = Trade_items(
        component_item_id=comp_item_id,
        component_id=form.component_id,
        quantity=form.quantity,
        price=narx,
        trade_id=form.trade_id,
        material_id=form.material2_id,
        user_id=user.id,
        order_id=order_ver.id
    )
    db.add(new_trade_item_db)
    db.commit()
    db.refresh(new_trade_item_db)

    if form.size1 or form.size2 or form.comment:

        new_trade_item_size_db = Trade_items_size(
            trade_item_id=new_trade_item_db.id,
            size1=form.size1,
            size2=form.size2,
            comment=form.comment
        )
        db.add(new_trade_item_size_db)
        db.commit()
        db.refresh(new_trade_item_size_db)


    if new_trade_item_db.component_item.product_id > 0:

        that_plan = Plan(
            product_id=new_trade_item_db.component_item.product_id,
            material_id=new_trade_item_db.material_id,
            order_id=new_trade_item_db.order_id,
            trade_id=new_trade_item_db.trade_id,
            trade_item_id=new_trade_item_db.id,
            value=new_trade_item_db.quantity,
            rest_value=new_trade_item_db.quantity,
            comment=form.comment,
            size1=form.size1,
            size2=form.size2,
            to_date=new_trade_item_db.trade.order.delivery_date,
        )
        
        create_plans_for_order(that_plan, user, db, False)

                


def delete_component_item_from_pre_order(id, db: Session, user):
    trade_item_verification = db.query(
        Trade_items).filter(Trade_items.id == id).first()
    if trade_item_verification is None:
        raise HTTPException(
            status_code=400, detail="Bunday id raqamli savdo mavjud emas")
    order_ver = db.query(Orders).filter(Orders.id == one_trade(
        trade_item_verification.trade_id, 0, db).Trades.order_id, Orders.market_id == user.market_id).first()
    if order_ver is None or order_ver.status != "pre_order":
        raise HTTPException(
            status_code=400, detail="Ushbu buyurtma yakunlangan")

    db.query(Product_Store).filter(Product_Store.trade_id == trade_item_verification.trade_id, Product_Store.trade_item_id ==
                                   trade_item_verification.id).update({Product_Store.trade_id: 0, Product_Store.trade_item_id: 0})
    db.query(Cycle_Store).filter(Cycle_Store.trade_id == trade_item_verification.trade_id, Cycle_Store.trade_item_id ==
                                 trade_item_verification.id).update({Cycle_Store.trade_id: 0, Cycle_Store.trade_item_id: 0})

    db.query(Plan).filter(Plan.trade_item_id==trade_item_verification.id).delete()
    db.delete(trade_item_verification)
    db.commit()
