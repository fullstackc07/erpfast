from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date


class Phone(BaseModel):
    phone: str


class UpdatePhone(BaseModel):
    id: int
    phone: str


class Customer(BaseModel):
    name: str
    type: str
    phones: List[Phone]


class UpdateCustomer(BaseModel):
    id: int
    name: str
    type: str
    phones: List[UpdatePhone]


class Expense(BaseModel):
    money: float = Field(..., ge=0.1)
    type: str
    source: int
    comment: str
    kassa_id: int


class Fixed_expense(BaseModel):
    name: str


class Market(BaseModel):
    name: str
    address: str
    phones: List[Phone]


class UpdateMarket(BaseModel):
    id: int
    name: str
    address: str
    phones: List[UpdatePhone]


class UpdateFixed_expense(BaseModel):
    id: int
    name: str


class Income_for_loan(BaseModel):
    money: float = Field(..., ge=0.1)
    source: int
    comment: str


class Kassa(BaseModel):
    name: str
    comment: str


class UpdateKassa(BaseModel):
    id: int
    name: str
    comment: str


class Take_money_from_user(BaseModel):
    money: float = Field(..., ge=0.1)
    user_id: int
    kassa_id: int
    comment: str


class Order(BaseModel):
    status: str
    delivery_date: date = None
    customer_id: int


class OrderConfirmation(BaseModel):
    id: int
    money: float = Field(..., ge=0)
    discount: float = Field(..., ge=0)
    customer_id: int
    loan_repayment_date: Optional[date] = None


class Attach_customer_to_order(BaseModel):
    id: int
    customer_id: int


class Update_delivery_date_for_pre_order(BaseModel):
    id: int
    delivery_date: date


class Trade(BaseModel):
    product_store_pr_id: int
    material_id: int
    quantity: float = Field(..., ge=0.1)
    price: float = Field(..., ge=0.1)
    discount: Optional[float] = Field(..., ge=0)
    order_id: int
    size1: float
    size2: float


class Return_product(BaseModel):
    trade_id: int
    quantity: float = Field(..., ge=0.1)
    price: Optional[float] = Field(..., ge=0.1)
    kassa_id: int


class Trade_pr_to_pre_order(BaseModel):
    product_id: int
    quantity: float = Field(..., ge=0.1)
    price: float = Field(..., ge=0)
    discount: Optional[float] = Field(..., ge=0)
    order_id: int


class Trade_comp_item_to_pre_order(BaseModel):
    component_id: int
    material_id: Optional[int] = Field(0, ge=0)
    product_id: int
    quantity: float = Field(..., ge=0.1)
    material2_id: Optional[int] = Field(0, ge=0)
    price: float = Field(..., ge=0.1)
    trade_id: int
    size1: float = 0
    size2: float = 0
    comment: str
    order_id: int


class Product_control(BaseModel):
    product_id: int
    size1: float
    size2: float
    real_quantity: float