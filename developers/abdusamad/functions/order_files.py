from fastapi import HTTPException
from ..models import Order_files
import os
from .orders import one_order


def all_order_files(order_id, db):
    return db.query(Order_files).filter(Order_files.order_id == order_id).order_by(Order_files.id.desc()).all()


def create_order_file(file, comment, order_id, user, db):
    order_files_verification = db.query(Order_files).filter(Order_files.file == file, Order_files.order_id == order_id).first()
    if order_files_verification :
        raise HTTPException(status_code = 400, detail = "Bunday fayl mavjud")
    if one_order(order_id, db) is None or one_order(order_id, db).market_id != user.market_id :
        raise HTTPException(status_code = 400, detail = "Bunday buyurtma mavjud emas")
    file_location = file.filename
    ext = os.path.splitext(file_location)[-1].lower()
    if ext not in [".jpg", ".png"] :
        raise HTTPException(status_code = 400, detail = "Yuklanayotgan fayl formatiga ruhsat berilmagan")
    with open(f"assets/order_files/{file_location}", "wb+") as file_object:
        file_object.write(file.file.read())
    new_file_db = Order_files(
        file = file_location,
        comment = comment,
        order_id = order_id,
        user_id = user.id
    )
    db.add(new_file_db)
    db.commit()
    db.refresh(new_file_db)
    return new_file_db


def delete_order_file(id, db, user) :
    order_ver = db.query(Order_files).filter(Order_files.id == id).first()
    if order_ver is None :
        raise HTTPException(status_code = 400, detail = "Bunday id raqamli fayl mavjud emas")
    if one_order(order_ver.order_id, db) is None or one_order(order_ver.order_id, db).market_id != user.market_id :
        raise HTTPException(status_code = 400, detail = "Bunday buyurtma mavjud emas")
    db.delete(order_ver)
    db.commit()