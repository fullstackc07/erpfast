from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from databases.main import ActiveSession
from sqlalchemy import func, and_
from security.auth import get_current_active_user
from ..models import Controls, Products_control
from ..schemas import Product_control
from ...yusufjon.models.product import Product
from ...yusufjon.models.product_type import Product_Type
from ...yusufjon.models.olchov import Olchov
from ...yusufjon.models.product_store import Product_Store
from developers.yusufjon.schemas.user import NewUser
from datetime import datetime
import math


products_control_router = APIRouter(tags=['Products_control'])


@products_control_router.get("/get_controls")
def get_controls(market_id: int = 0, page: int = 1, limit: int = 25, db: Session = ActiveSession, current_user: NewUser = Depends(get_current_active_user)):
    if page <= 0 or limit < 0 :
        raise HTTPException(status_code = 400, detail = "page yoki limit 0 dan kichik kiritilmasligi kerak")
    if current_user.role != "seller_admin" :
        raise HTTPException(status_code = 400, detail = "Sizga ruhsat berilmagan")
    controls_data = db.query(Controls).filter(Controls.market_id == market_id, Controls.status == True)
    return {"current_page": page, "limit": limit, "pages": math.ceil(controls_data.count() / limit), "data": controls_data.order_by(Controls.id.desc()).offset((page - 1) * limit).limit(limit).all()}


@products_control_router.get("/get_products_control")
def get_products_control(control_id: int = 0, status: str = None, pr_id: int = 0, size1: float = 0, size2: float = 0, page: int = 1, limit: int = 25, db: Session = ActiveSession, current_user: NewUser = Depends(get_current_active_user)):
    if page <= 0 or limit < 0 :
        raise HTTPException(status_code = 400, detail = "page yoki limit 0 dan kichik kiritilmasligi kerak")
    if current_user.role != "seller_admin" :
        raise HTTPException(status_code = 400, detail = "Sizga ruhsat berilmagan")
    elif status == "counted" :
        quantity_filter = Products_control.real_quantity > 0
    elif status == "not_counted" :
        quantity_filter = Products_control.real_quantity == 0
    elif status == "not_equal" and current_user.role == "branch_admin" :
        quantity_filter = Products_control.real_quantity != Products_control.quantity
    elif status == "confirmed" :
        quantity_filter = Products_control.status == True
    else :
        raise HTTPException(status_code = 400, detail = "Statusda xatolik")
    if control_id != 0 :
        control_filter = Products_control.control_id == control_id
    else :
        control_verification = db.query(Controls).filter(Controls.market_id == current_user.market_id, Controls.status == False).first()
        if control_verification :
            control_filter = Products_control.control_id == control_verification.id
        else :
            control_filter = Products_control.control_id == 0
    if pr_id != 0 :
        product_filter = Products_control.product_id == pr_id
    else :
        product_filter = Products_control.product_id > 0
    if size1 and size2 :
        size_filter = and_(Products_control.size1 == size1, Products_control.size2 == size2)
    else :
        size_filter = Products_control.product_id > 0
    products_control_data = db.query(Products_control.id.label("id"), Products_control.size1.label("size1"), Products_control.size2.label("size2"), Products_control.real_quantity.label("real_quantity"), Products_control.quantity.label("quantity"), Product.name.label("pr_name"), Product_Type.name.label("pr_type_name"), Olchov.name.label("olchov")).outerjoin((Product, Product.id == Products_control.product_id), (Product_Type, Product_Type.id == Product.product_type_id), (Olchov, Olchov.id == Product_Type.olchov_id)).filter(quantity_filter, control_filter, product_filter, size_filter)
    return {"current_page": page, "limit": limit, "pages": math.ceil(products_control_data.count() / limit), "data": products_control_data.order_by(Product.name.asc()).offset((page - 1) * limit).limit(limit).all()}
    
    
@products_control_router.post("/create_control")
def create_control(db: Session = ActiveSession, current_user: NewUser = Depends(get_current_active_user)):
    if current_user.role != "seller_admin" :
        raise HTTPException(status_code = 400, detail = "Sizga ruhsat berilmagan")
    control_verification = db.query(Controls).filter(Controls.market_id == current_user.market_id, Controls.status == False).first()
    if control_verification :
        raise HTTPException(status_code = 400, detail = "Yakunlanmagan invertarizatsiya mavjud")
    new_control_db = Controls(
        time = datetime.now(),
        status = False,
        user_id = current_user.id,
        market_id = current_user.market_id
    )
    db.add(new_control_db)
    db.commit()
    db.refresh(new_control_db)
    products = db.query(Product_Store, func.sum(Product_Store.value).label("sum_quantity")).filter(Product_Store.value > 0, Product_Store.market_id == current_user.market_id).group_by(Product_Store.product_id, Product_Store.size1, Product_Store.size2).all()
    for product in products :
        new_product_control_db = Products_control(
            product_id = product.Product_Store.product_id,
            size1 = product.Product_Store.size1,
            size2 = product.Product_Store.size2,
            quantity = product.sum_quantity,
            real_quantity = 0,
            user_id = current_user.id,
            market_id = current_user.market_id,
            control_id = new_control_db.id
        )
        db.add(new_product_control_db)
        db.commit()
        db.refresh(new_product_control_db)
    raise HTTPException(status_code = 200, detail = "Amaliyot muvaffaqiyatli bajarildi")
    
    
@products_control_router.delete("/remove_control")
def remove_control(db: Session = ActiveSession, current_user: NewUser = Depends(get_current_active_user)):
    if current_user.role != "seller_admin" :
        raise HTTPException(status_code = 400, detail = "Sizga ruhsat berilmagan")
    control_verification = db.query(Controls).filter(Controls.market_id == current_user.market_id, Controls.status == False, Controls.user_id == current_user.id).first()
    if control_verification is None :
        raise HTTPException(status_code = 400, detail = "Amaldagi invertarizatsiya mavjud emas yoki boshqa admin tomonidan yoqilgan")
    products_control = db.query(Products_control).filter(Products_control.status == False, Products_control.real_quantity > 0, Products_control.market_id == current_user.market_id, Products_control.control_id == control_verification.id)
    if products_control.first() :
        raise HTTPException(status_code = 400, detail = "Ushbu invertarizatsiya orqali mahsulot sanog'i boshlangan")
    db.delete(control_verification)
    db.query(Products_control).filter(Products_control.market_id == current_user.market_id, Products_control.control_id == control_verification.id).delete()
    db.commit()
    raise HTTPException(status_code = 200, detail = "Amaliyot muvaffaqiyatli bajarildi")


@products_control_router.put("/update_product_control")
def update_product_control(this_product_control: Product_control, db: Session = ActiveSession, current_user: NewUser = Depends(get_current_active_user)):
    if current_user.role != "seller_admin" :
        raise HTTPException(status_code = 400, detail = "Sizga ruhsat berilmagan")
    control_verification = db.query(Controls).filter(Controls.market_id == current_user.market_id, Controls.status == False).first()
    if control_verification is None :
        raise HTTPException(status_code = 400, detail = "Amaldagi invertarizatsiya mavjud emas")
    products_control_verification = db.query(Products_control).filter(Products_control.product_id == this_product_control.product_id, Products_control.size1 == this_product_control.size1, Products_control.size2 == this_product_control.size2, Products_control.market_id == current_user.market_id, Products_control.control_id == control_verification.id).first()
    if products_control_verification is None :
        raise HTTPException(status_code = 400, detail = "Bunday mahsulot mavjud emas")
    if this_product_control.real_quantity < 0 :
        raise HTTPException(status_code = 400, detail = "Mahsulot soni 0 dan katta kiritilishi kerak")
    db.query(Products_control).filter(Products_control.id == products_control_verification.id).update({
        Products_control.real_quantity: this_product_control.real_quantity,
        Products_control.user_id: current_user.id
    })
    db.commit()
    raise HTTPException(status_code = 200, detail = "Ma'lumotlar muvaffaqiyatli o'zgartirildi")


@products_control_router.put("/change_product_quantity")
def change_product_quantity(db: Session = ActiveSession, current_user: NewUser = Depends(get_current_active_user)):
    if current_user.role != "seller_admin" :
        raise HTTPException(status_code = 400, detail = "Sizga ruhsat berilmagan")
    control_verification = db.query(Controls).filter(Controls.market_id == current_user.market_id, Controls.status == False).first()
    if control_verification is None :
        raise HTTPException(status_code = 400, detail = "Invertarizatsiya yakunlangan")
    this_product_control = db.query(Products_control).filter(Products_control.control_id == control_verification.id, Products_control.market_id == current_user.market_id, (Products_control.real_quantity <= 0) | (Products_control.real_quantity > Products_control.quantity)).first()
    if this_product_control :
        raise HTTPException(status_code = 400, detail = "Mahsulotlar ro'yxatida sanog'i yakunlanmaganlar borligi sababli yakunlab bo'lmaydi")
    products = db.query(Products_control).filter(Products_control.control_id == control_verification.id, Products_control.market_id == current_user.market_id).all()
    for product in products :
        this_product = db.query(Product_Store).filter(Product_Store.product_id == product.product_id, Product_Store.size1 == product.size1, Product_Store.size2 == product.size2, Product_Store.market_id == current_user.market_id).order_by(Product_Store.id.asc()).first()
        db.query(Product_Store).filter(Product_Store.id == this_product.id).update({
            Product_Store.value: product.real_quantity
        })
        db.query(Products_control).filter(Products_control.id == product.id).update({
            Products_control.status: True
        })
        this_product_control = db.query(Products_control).filter(Products_control.market_id == current_user.market_id, Products_control.status == False).first()
        if this_product_control is None :
            db.query(Controls).filter(Controls.id == control_verification.id).update({
                Controls.status: True
            })
        db.commit()
    raise HTTPException(status_code = 200, detail = "Ma'lumotlar muvaffaqiyatli o'zgartirildi")