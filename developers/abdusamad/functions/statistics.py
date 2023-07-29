from ..models import Expenses, Incomes, Orders, Returned_products, Trades
from ...yusufjon.models.product_store import Product_Store
from ...yusufjon.models.product import Product
from sqlalchemy import func


def statistics(from_time, to_time, market_id, db):
    if market_id > 0 :
        sum_expense = db.query(func.coalesce(func.sum(Expenses.money), 0)).filter(func.date(Expenses.time).between(from_time, to_time), Expenses.market_id == market_id).scalar()
        sum_income = db.query(func.coalesce(func.sum(Incomes.money), 0)).filter(func.date(Expenses.time).between(from_time, to_time), Expenses.market_id == market_id).scalar()
        sum_order_discount = db.query(func.coalesce(func.sum(Orders.discount), 0)).filter(func.date(Orders.time).between(from_time, to_time), Orders.market_id == market_id).scalar()
        orders = db.query(Orders).filter(Orders.market_id == market_id).all()
        orders_between_time = db.query(Orders).filter(func.date(Orders.time).between(from_time, to_time), Orders.market_id == market_id).all()
        sum_returned_price = db.query(func.coalesce(func.sum(Returned_products.quantity * Returned_products.price), 0)).filter(func.date(Returned_products.time).between(from_time, to_time), Returned_products.order_id.in_([order.id for order in orders])).scalar()
        sum_trade_discount = db.query(func.coalesce(func.sum(Trades.quantity * Trades.discount), 0)).filter(Trades.order_id.in_([order.id for order in orders_between_time])).scalar()
        sum_trade_price = db.query(func.coalesce(func.sum(Trades.quantity * Trades.price), 0)).filter(Trades.order_id.in_([order.id for order in orders_between_time])).scalar()
        sum_trade_tan_narx = db.query(func.coalesce(func.sum(Trades.quantity * Product.plant_price), 0) + func.coalesce(func.sum(Trades.quantity * Product_Store.price), 0)).outerjoin((Product, Product.id == Trades.product_id), (Product_Store, Product_Store.id == Trades.product_store_id)).filter(Trades.order_id.in_([order.id for order in orders_between_time])).scalar()
        return {
            "sum_expense": sum_expense,
            "sum_income": sum_income,
            "sum_order_discount": sum_order_discount,
            "sum_returned_price": sum_returned_price,
            "sum_trade_discount": sum_trade_discount,
            "sum_trade_price": sum_trade_price,
            "sum_trade_tan_narx": sum_trade_tan_narx
            }
    else :
        sum_expense = db.query(func.coalesce(func.sum(Expenses.money), 0)).filter(func.date(Expenses.time).between(from_time, to_time), Expenses.market_id > 0).scalar()
        sum_income = db.query(func.coalesce(func.sum(Incomes.money), 0)).filter(func.date(Expenses.time).between(from_time, to_time), Expenses.market_id > 0).scalar()
        sum_order_discount = db.query(func.coalesce(func.sum(Orders.discount), 0)).filter(func.date(Orders.time).between(from_time, to_time), Orders.market_id > 0).scalar()
        orders = db.query(Orders).filter(Orders.market_id > 0).all()
        orders_between_time = db.query(Orders).filter(func.date(Orders.time).between(from_time, to_time), Orders.market_id > 0).all()
        sum_returned_price = db.query(func.coalesce(func.sum(Returned_products.quantity * Returned_products.price), 0)).filter(func.date(Returned_products.time).between(from_time, to_time), Returned_products.order_id.in_([order.id for order in orders])).scalar()
        sum_trade_discount = db.query(func.coalesce(func.sum(Trades.quantity * Trades.discount), 0)).filter(Trades.order_id.in_([order.id for order in orders_between_time])).scalar()
        sum_trade_price = db.query(func.coalesce(func.sum(Trades.quantity * Trades.price), 0)).filter(Trades.order_id.in_([order.id for order in orders_between_time])).scalar()
        sum_trade_tan_narx = db.query(func.coalesce(func.sum(Trades.quantity * Product.plant_price), 0) + func.coalesce(func.sum(Trades.quantity * Product_Store.price), 0)).outerjoin((Product, Product.id == Trades.product_id), (Product_Store, Product_Store.id == Trades.product_store_id)).filter(Trades.order_id.in_([order.id for order in orders_between_time])).scalar()
        return {
            "sum_expense": sum_expense,
            "sum_income": sum_income,
            "sum_order_discount": sum_order_discount,
            "sum_returned_price": sum_returned_price,
            "sum_trade_discount": sum_trade_discount,
            "sum_trade_price": sum_trade_price,
            "sum_trade_tan_narx": sum_trade_tan_narx
            }



def top_product_statistics(from_time, to_time, product_id, market_id, limit, db):
    if from_time and to_time :
        time_filter = func.date(Orders.time).between(from_time, to_time)
    else :  
        time_filter = Orders.id > 0
    orders = db.query(Orders).filter(Orders.market_id == market_id, time_filter).all()
    if product_id :
        returned_products = db.query(func.coalesce(func.sum(Returned_products.quantity), 0).label("sum_returned_quantity")).filter(Returned_products.order_id.in_([order.id for order in orders])).limit(limit).all()
        trades = db.query(func.coalesce(func.sum(Trades.quantity), 0).label("sum_trade_quantity")).filter(Trades.order_id.in_([order.id for order in orders])).limit(limit).all()
    else :
        returned_products = db.query(func.coalesce(func.sum(Returned_products.quantity), 0).label("sum_returned_quantity")).filter(Returned_products.order_id.in_([order.id for order in orders])).limit(limit).all()
        trades = db.query(func.coalesce(func.sum(Trades.quantity), 0).label("sum_trade_quantity")).filter(Trades.order_id.in_([order.id for order in orders])).limit(limit).all()
    return {
        "returned_products": returned_products,
        "trades": trades
        }