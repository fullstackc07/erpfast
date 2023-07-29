from databases.main import Base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, Boolean, ForeignKey, and_, Text
from datetime import datetime
from developers.yusufjon.models.user import User
from developers.yusufjon.models.product_store import Product_Store
from developers.yusufjon.models.product import Product
from developers.yusufjon.models.component_item import Component_Item
from developers.yusufjon.models.material import Material


class Customers(Base):
    __tablename__ = "customers"
    id = Column(Integer, autoincrement = True, primary_key = True)
    name = Column(String)
    type = Column(String)
    user_id = Column(Integer)
    market_id = Column(Integer)
    
    user = relationship('User', foreign_keys=[user_id], primaryjoin=lambda: and_(User.id == Customers.user_id))
    market = relationship('Markets', foreign_keys=[market_id], primaryjoin=lambda: and_(Markets.id == Customers.market_id))


class Expenses(Base):
    __tablename__ = "expenses"
    id = Column(Integer, autoincrement = True, primary_key = True)
    money = Column(Numeric)
    type = Column(String)
    source = Column(Integer)
    time = Column(DateTime, default = datetime.now())
    comment = Column(String)
    kassa_id = Column(Integer)
    user_id = Column(Integer)
    market_id = Column(Integer)
    salary_id = Column(Integer, ForeignKey("salary.id"), default=0)

    salary = relationship("Salary")

    fixed_expense = relationship('Fixed_expenses', foreign_keys=[source], primaryjoin=lambda: and_(Fixed_expenses.id == Expenses.source, Expenses.type == 'fixed_expense'))
    kassa = relationship('Kassa', foreign_keys=[kassa_id], primaryjoin=lambda: and_(Kassa.id == Expenses.kassa_id))
    user = relationship('User', foreign_keys=[user_id], primaryjoin=lambda: and_(User.id == Expenses.user_id))
    market = relationship('Markets', foreign_keys=[market_id], primaryjoin=lambda: and_(Markets.id == Expenses.market_id))


class Fixed_expenses(Base):
    __tablename__ = "fixed_expenses"
    id = Column(Integer, autoincrement = True, primary_key = True)
    name = Column(String)
    user_id = Column(Integer)
    market_id = Column(Integer)

    user = relationship('User', foreign_keys=[user_id], primaryjoin=lambda: and_(User.id == Fixed_expenses.user_id))
    market = relationship('Markets', foreign_keys=[market_id], primaryjoin=lambda: and_(Markets.id == Fixed_expenses.market_id))


class Galery(Base):
    __tablename__ = "galery"
    id = Column(Integer, autoincrement = True, primary_key = True)
    file = Column(Text)
    user_id = Column(Integer)
    comment = Column(Integer)
    market_id = Column(Integer)
    
    market = relationship('Markets', foreign_keys=[market_id], primaryjoin=lambda: and_(Markets.id == Galery.market_id))


class Incomes(Base):
    __tablename__ = "incomes"
    id = Column(Integer, autoincrement = True, primary_key = True)
    money = Column(Numeric)
    type = Column(String)
    source = Column(Integer)
    time = Column(DateTime, default = datetime.now())
    comment = Column(String)
    user_id = Column(Integer)
    kassa_id = Column(Integer, default = 0)
    market_id = Column(Integer)
    
    order = relationship('Orders', foreign_keys=[source], primaryjoin=lambda: and_(Orders.id == Incomes.source, Incomes.type == "order"))
    loan = relationship('Loans', foreign_keys=[source], primaryjoin=lambda: and_(Loans.id == Incomes.source, Incomes.type == "loan"))
    kassa = relationship('Kassa', foreign_keys=[kassa_id], primaryjoin=lambda: Kassa.id == Incomes.kassa_id)
    user = relationship('User', foreign_keys=[user_id], primaryjoin=lambda: and_(User.id == Incomes.user_id))
    market = relationship('Markets', foreign_keys=[market_id], primaryjoin=lambda: and_(Markets.id == Incomes.market_id))


class Kassa(Base):
    __tablename__ = "kassa"
    id = Column(Integer, autoincrement = True, primary_key = True)
    name = Column(String)
    balance = Column(Numeric, default = 0)
    comment = Column(String)
    user_id = Column(Integer)
    market_id = Column(Integer)

    market = relationship('Markets', foreign_keys=[market_id], primaryjoin=lambda: and_(Markets.id == Kassa.market_id))
    

class Loans(Base):
    __tablename__ = "loans"
    id = Column(Integer, autoincrement = True, primary_key = True)
    money = Column(Numeric)
    residual = Column(Numeric)
    return_date = Column(Date)
    status = Column(Boolean, default = False)
    order_id = Column(Integer)
    market_id = Column(Integer)

    order = relationship('Orders', foreign_keys=[order_id], backref=backref('loans'), primaryjoin=lambda: and_(Orders.id == Loans.order_id))
    market = relationship('Markets', foreign_keys=[market_id], primaryjoin=lambda: and_(Markets.id == Loans.market_id))
    

class Markets(Base):
    __tablename__ = "markets"
    id = Column(Integer, autoincrement = True, primary_key = True)
    name = Column(String)
    address = Column(String)
    user_id = Column(Integer)

    user = relationship('User', foreign_keys=[user_id], primaryjoin=lambda: and_(User.id == Markets.user_id))


class Orders(Base):
    __tablename__ = "orders"
    id = Column(Integer, autoincrement = True, primary_key = True)
    ordinal_number = Column(Integer)
    time = Column(DateTime, default = datetime.now())
    delivery_date = Column(Date, default = 0)
    discount = Column(Numeric, default = 0)
    status = Column(String)
    customer_id = Column(Integer, default = 0)
    user_id = Column(Integer)
    market_id = Column(Integer, ForeignKey("markets.id"), default = 0)

    market = relationship('Markets')
    customer = relationship('Customers', foreign_keys=[customer_id], primaryjoin=lambda: and_(Customers.id == Orders.customer_id))
    user = relationship('User', foreign_keys=[user_id], primaryjoin=lambda: and_(User.id == Orders.user_id))


class Order_files(Base):
    __tablename__ = "order_files"
    id = Column(Integer, autoincrement = True, primary_key = True)
    file = Column(Text)
    comment = Column(String)
    order_id = Column(Integer)
    user_id = Column(Integer)

    order = relationship('Orders', foreign_keys=[order_id], backref=backref('files', lazy="joined"), primaryjoin=lambda: Order_files.order_id == Orders.id)


class Returned_products(Base):
    __tablename__ = "returned_products"
    id = Column(Integer, autoincrement = True, primary_key = True)
    trade_id = Column(Integer)
    related_number = Column(Integer)
    order_id = Column(Integer)
    quantity = Column(Numeric)
    price = Column(Numeric)
    time = Column(Date)
    user_id = Column(Integer)

    trade = relationship('Trades', foreign_keys=[trade_id], backref=backref('returned_products'), primaryjoin=lambda: Returned_products.trade_id == Trades.id)


class Trades(Base):
    __tablename__ = "trades"
    id = Column(Integer, autoincrement = True, primary_key = True)
    product_store_id = Column(Integer, default = 0)
    product_id = Column(Integer, default = 0)
    quantity = Column(Numeric)
    price = Column(Numeric, default = 0)
    discount = Column(Numeric, default = 0)
    related_number = Column(Integer, default = 0)
    order_id = Column(Integer)
    user_id = Column(Integer)

    product_store = relationship('Product_Store', foreign_keys=[product_store_id], primaryjoin=lambda: Product_Store.id == Trades.product_store_id)
    product = relationship('Product', foreign_keys=[product_id], primaryjoin=lambda: Product.id == Trades.product_id)
    order = relationship('Orders', foreign_keys=[order_id], primaryjoin=lambda: Orders.id == Trades.order_id, backref='trades')
    user = relationship('User', foreign_keys=[user_id], primaryjoin=lambda: User.id == Trades.user_id)


class Trade_items(Base):
    __tablename__ = "trade_items"
    id = Column(Integer, autoincrement = True, primary_key = True)
    component_item_id = Column(Integer)
    component_id = Column(Integer, ForeignKey("component.id"))
    material_id = Column(Integer, ForeignKey("material.id"))
    order_id = Column(Integer, ForeignKey("orders.id"))
    quantity = Column(Numeric)
    trade_id = Column(Integer)
    user_id = Column(Integer)
    price = Column(Numeric, default = 0)
    
    component = relationship('Component', backref='trade_items')
    material = relationship('Material', lazy='joined')
    order = relationship('Orders')
    component_item = relationship('Component_Item', foreign_keys=[component_item_id], primaryjoin=lambda: and_(Component_Item.id == Trade_items.component_item_id), backref="trade_items")
    user = relationship('User', foreign_keys=[user_id], primaryjoin=lambda: and_(User.id == Trade_items.user_id))
    trade = relationship('Trades', foreign_keys=[trade_id], backref=backref('trade_items'), primaryjoin=lambda: Trades.id == Trade_items.trade_id)


class Trade_items_size(Base):
    __tablename__ = "trade_items_size"
    id = Column(Integer, autoincrement = True, primary_key = True)
    trade_item_id = Column(Integer)
    size1 = Column(Numeric)
    size2 = Column(Numeric)
    comment = Column(String)
    
    trade_item = relationship('Trade_items', foreign_keys=[trade_item_id], backref=backref('trade_items_size', lazy="joined"), primaryjoin=lambda: Trade_items_size.trade_item_id == Trade_items.id)


class Controls(Base):
    __tablename__ = "controls"
    id = Column(Integer, autoincrement = True, primary_key = True)
    time = Column(DateTime)
    status = Column(Boolean, default = False)
    user_id = Column(Integer)
    market_id = Column(Integer)


class Products_control(Base):
    __tablename__ = "products_control"
    id = Column(Integer, autoincrement = True, primary_key = True)
    product_id = Column(Integer)
    size1 = Column(Numeric)
    size2 = Column(Numeric)
    quantity = Column(Numeric)
    real_quantity = Column(Numeric)
    user_id = Column(Integer)
    market_id = Column(Integer)
    control_id = Column(Integer)
    status = Column(Boolean, default = False)