from fastapi import HTTPException
from ..models import Orders, Incomes, Loans, Trades, Expenses, Customers, Trade_items
from ...yusufjon.models.product_store import Product_Store
from ...yusufjon.models.component_item import Component_Item
from ...yusufjon.models.material_store import Material_Store
from sqlalchemy import func
import math
from datetime import datetime
from .trades import one_trade
from .customers import one_customer
from sqlalchemy.orm import joinedload
from developers.yusufjon.models.user import User


def sum_income(source, type, db):
    return db.query(func.coalesce(func.sum(Incomes.money), 0)).filter(Incomes.source == source, Incomes.type == type).scalar()


def sum_expense(source, type, db):
    return db.query(func.coalesce(func.sum(Expenses.money), 0)).filter(Expenses.source == source, Expenses.type == type).scalar()


def all_orders(from_time, to_time, customer_id, user_id, status, market_id, page, limit, db):
    if from_time and to_time :
        time_filter = func.date(Orders.time).between(from_time, to_time)
    else :
        time_filter = Orders.id > 0
    if customer_id :
        customer_filter = Orders.customer_id == customer_id
    else :
        customer_filter = Orders.id > 0
    if user_id :
        user_filter = Orders.user.id == user_id
    else :
        user_filter = Orders.id > 0
    if status :
        status_filter = Orders.status == status
    else :
        status_filter = Orders.id > 0
    orders = db.query(Orders).options(joinedload(Orders.customer), joinedload(Orders.user)).filter(time_filter, customer_filter, user_filter, status_filter, Orders.market_id == market_id)
    return {"current_page": page, "limit": limit, "pages": math.ceil(orders.count() / limit), "data": orders.offset((page - 1) * limit).limit(limit).all()}


def one_order(id, db):
    return db.query(Orders).options(joinedload(Orders.customer), joinedload(Orders.user)).filter(Orders.id == id).first()


def one_order2(id, db):
    return {"order": db.query(Orders).options(joinedload(Orders.customer), joinedload(Orders.user)).filter(Orders.id == id).first(), "sum_income": db.query(func.coalesce(func.sum(Incomes.money), 0)).filter(Incomes.source == id, Incomes.type == "order").scalar()}


def create_order(form, user, db):
    today_last_ordinal_number = db.query(Orders).filter(func.date(Orders.time) == datetime.now().date(), Orders.market_id == user.market_id).order_by(Orders.ordinal_number.desc()).first()
    if today_last_ordinal_number :
        ordinal_number = today_last_ordinal_number.ordinal_number + 1
    else :
        ordinal_number = 1
    if form.status not in ["false", "pre_order"] :
        raise HTTPException(status_code = 400, detail = "Bunday status mavjud emas")
    if form.customer_id :
        if one_customer(form.customer_id, db) is None or one_customer(form.customer_id, db).market_id != user.market_id :
            raise HTTPException(status_code = 400, detail = "Bunday mijoz mavjud emas")
    new_order_db = Orders(
        ordinal_number = ordinal_number,
        delivery_date = form.delivery_date,
        status = form.status,
        customer_id = form.customer_id,
        user_id = user.id,
        market_id = user.market_id,
    )
    db.add(new_order_db)
    db.commit()
    db.refresh(new_order_db)
    return new_order_db


def delete_order(id, db, user):
    if one_order(id, db) is None or one_order(id, db).market_id != user.market_id :
        raise HTTPException(status_code = 400, detail = "Ushbu buyurtmani o'chirib bo'lmaydi")
    if one_trade(0, id, db) and one_trade(0, id, db) > 0 :
        raise HTTPException(status_code = 400, detail = "Buyurtmani o'chirishdan oldin unga biriktirilgan mahsulotlar o'chirilishi kerak")
    db.delete(one_order(id, db))
    db.commit()


def order_confirmation(form, user, db):
    if one_order(form.id, db) is None or one_order(form.id, db).market_id != user.market_id or one_order(form.id, db).status == "true" :
        raise HTTPException(status_code = 400, detail = "Bunday buyurtma mavjud emas yoki yakunlangan")
    if one_order(form.id, db).status == "false" :
        if one_trade(0, form.id, db) and one_trade(0, form.id, db) > form.money + form.discount :
            if one_order(form.id, db).customer_id == 0 and form.customer_id == 0 :
                raise HTTPException(status_code = 400, detail = "Nasiya faqat mijozga biriktirilishi mumkin")
            elif one_order(form.id, db).customer_id == 0 and form.customer_id > 0 :
                if one_customer(form.customer_id, db) is None or one_customer(form.customer_id, db).market_id != user.market_id :
                    raise HTTPException(status_code = 400, detail = "Bunday mijoz mavjud emas")
                db.query(Orders).filter(Orders.id == form.id).update({
                    Orders.customer_id: form.customer_id,
                    Orders.user_id: user.id
                })
                db.commit()
            if form.money > 0 :
                new_income_db = Incomes(
                    money = form.money,
                    type = "order",
                    source = form.id,
                    comment = "",
                    user_id = user.id,
                    market_id = user.market_id,
                )
                db.query(User).filter(User.id == user.id).update({
                    User.balance: User.balance + form.money
                })
                db.add(new_income_db)
                db.commit() 
                db.refresh(new_income_db)
            new_loan_db = Loans(
                money = one_trade(0, form.id, db) - (form.money + form.discount),
                residual = one_trade(0, form.id, db) - (form.money + form.discount),
                return_date = form.loan_repayment_date,
                order_id = form.id,
                market_id = user.market_id
            )
            db.add(new_loan_db)
            db.commit()
            db.refresh(new_loan_db)
            db.query(Orders).filter(Orders.id == form.id).update({
                Orders.discount: form.discount,
                Orders.status: "true",
                Orders.user_id: user.id
            })
            db.commit() 
        elif one_trade(0, form.id, db) and one_trade(0, form.id, db) == form.money + form.discount :
            new_income_db = Incomes(
                money = form.money,
                type = "order",
                source = form.id,
                comment = "",
                user_id = user.id,
                market_id = user.market_id
            )
            db.query(User).filter(User.id == user.id).update({
                User.balance: User.balance + form.money
            })
            db.add(new_income_db)
            db.commit() 
            db.refresh(new_income_db)
            db.query(Orders).filter(Orders.id == form.id).update({
                Orders.discount: form.discount,
                Orders.status: "true",
                Orders.user_id: user.id
            })
            db.commit() 
    elif one_order(form.id, db).status == "pre_order" :
        trades = db.query(Trades).filter(Trades.order_id == one_order(form.id, db).id).all()
        for trade in trades :
            trade_items = db.query(Trade_items).filter(Trade_items.trade_id == trade.id).all()
            for trade_item in trade_items :
                comp_item = db.query(Component_Item).filter(Component_Item.id == trade_item.component_item_id).first()
                if comp_item.product_id and comp_item.product_id > 0 :
                    product_store_verification = db.query(Product_Store).filter(Product_Store.trade_id == trade.id, Product_Store.product_id == comp_item.product_id, Product_Store.trade_item_id == trade_item.id).first()
                    if product_store_verification is None or product_store_verification.value < trade_item.quantity :
                        raise HTTPException(status_code = 400, detail = "Buyurtma olingan mahsulotdan yetarli hajmda mavjud emas")
                elif comp_item.material_id and comp_item.material_id > 0 :
                    material_store_verification = db.query(Material_Store).filter(Material_Store.material_id == comp_item.material_id, Material_Store.plant_id == 0).first()
                    if material_store_verification is None or material_store_verification.value < trade_item.quantity :
                        raise HTTPException(status_code = 400, detail = "Buyurtma olingan mahsulotdan yetarli hajmda mavjud emas")
        if one_trade(0, form.id, db) - sum_income(form.id, "order", db) < form.money + form.discount :
            raise HTTPException(status_code = 400, detail = "Olinayotgan pulda xatolik")
        for trade in trades :
            trade_items = db.query(Trade_items).filter(Trade_items.trade_id == trade.id).all()
            trade_item_sum_price = db.query(func.sum(Trade_items.price * Trade_items.quantity)).filter(Trade_items.trade_id == trade.id).scalar()
            for trade_item in trade_items :
                comp_item = db.query(Component_Item).filter(Component_Item.id == trade_item.component_item_id).first()
                if comp_item.product_id and comp_item.product_id > 0 :
                    product_store_verification = db.query(Product_Store).filter(Product_Store.trade_id == trade.id, Product_Store.product_id == comp_item.product_id, Product_Store.trade_item_id == trade_item.id).first()
                    db.query(Product_Store).filter(Product_Store.id == product_store_verification.id).update({
                        Product_Store.value: Product_Store.value - trade_item.quantity
                    })
                    db.commit()
                elif comp_item.material_id and comp_item.material_id > 0 :
                    mat_store = db.query(Material_Store).filter(Material_Store.material_id == comp_item.material_id, Material_Store.plant_id == 0).first()
                    db.query(Material_Store).filter(Material_Store.id == mat_store.id).update({
                        Material_Store.value: Material_Store.value - trade_item.quantity
                    })
                    db.commit()
            db.query(Trades).filter(Trades.id == trade.id).update({
                Trades.price: trade_item_sum_price
            })
            db.commit()
        if one_trade(0, form.id, db) - sum_income(form.id, "order", db) > form.money + form.discount :
            if one_order(form.id, db).customer_id == 0 and form.customer_id == 0 :
                raise HTTPException(status_code = 400, detail = "Nasiya faqat mijozga biriktirilishi mumkin")
            elif one_order(form.id, db).customer_id == 0 and form.customer_id > 0 :
                if one_customer(form.customer_id, db) is None or one_customer(form.customer_id, db).market_id != user.market_id :
                    raise HTTPException(status_code = 400, detail = "Bunday mijoz mavjud emas")
                db.query(Orders).filter(Orders.id == form.id).update({
                    Orders.customer_id: form.customer_id,
                    Orders.user_id: user.id
                })
                db.commit()
            if form.money > 0 :
                new_income_db = Incomes(
                    money = form.money,
                    type = "order",
                    source = form.id,
                    comment = "",
                    user_id = user.id,
                    market_id = user.market_id
                )
                db.query(User).filter(User.id == user.id).update({
                    User.balance: User.balance + form.money
                })
                db.add(new_income_db)
                db.commit() 
                db.refresh(new_income_db)
            new_loan_db = Loans(
                money = (one_trade(0, form.id, db) - sum_income(form.id, "order", db)) - (form.money + form.discount),
                residual = (one_trade(0, form.id, db) - sum_income(form.id, "order", db)) - (form.money + form.discount),
                return_date = form.loan_repayment_date,
                order_id = form.id,
                market_id = user.market_id
            )
            db.add(new_loan_db)
            db.refresh(new_loan_db)
            db.query(Orders).filter(Orders.id == form.id).update({
                Orders.discount: form.discount,
                Orders.status: "true",
                Orders.user_id: user.id
            })
            db.commit() 
        elif (one_trade(0, form.id, db) - sum_income(form.id, "order", db)) == form.money + form.discount :
            new_income_db = Incomes(
                money = form.money,
                type = "order",
                source = form.id,
                comment = "",
                user_id = user.id,
                market_id = user.market_id
            )
            db.query(User).filter(User.id == user.id).update({
                User.balance: User.balance + form.money
            })
            db.add(new_income_db)
            db.commit() 
            db.refresh(new_income_db)
            db.query(Orders).filter(Orders.id == form.id).update({
                Orders.discount: form.discount,
                Orders.status: "true",
                Orders.user_id: user.id
            })
            db.commit()

    raise HTTPException(status_code=200, detail="Ma'lumotlar saqlandi!")    
                

def attach_customer_to_order(form, user, db):
    if one_order(form.id, db) is None or one_order(form.id, db).market_id != user.market_id or one_order(form.id, db).status == "true" :
        raise HTTPException(status_code = 400, detail = "Bunday buyurtma mavjud emas yoki yakunlangan")
    if one_customer(form.customer_id, db) is None or one_customer(form.customer_id, db).market_id != user.market_id :
        raise HTTPException(status_code = 400, detail = "Bunday mijoz mavjud emas")
    db.query(Orders).filter(Orders.id == form.id).update({
        Orders.customer_id: form.customer_id,
        Orders.user_id: user.id
    })
    db.commit()
                

def update_delivery_date_for_pre_order(form, user, db):
    if one_order(form.id, db) is None or one_order(form.id, db).market_id != user.market_id or one_order(form.id, db).status != "pre_order" :
        raise HTTPException(status_code = 400, detail = "Bunday buyurtma mavjud emas yoki yakunlangan")
    db.query(Orders).filter(Orders.id == form.id).update({
        Orders.delivery_date: form.delivery_date,
        Orders.user_id: user.id
    })
    db.commit()