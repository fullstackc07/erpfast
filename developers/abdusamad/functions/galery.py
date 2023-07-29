from fastapi import HTTPException
from ..models import Galery
import os


def all_galery_files(market_id, db):
    return db.query(Galery).filter(Galery.market_id == market_id).order_by(Galery.id.desc()).all()


def create_galery_file(file, comment, user, db):
    galery_files_verification = db.query(Galery).filter(Galery.file == file, Galery.comment == comment, Galery.market_id == user.market_id).first()
    if galery_files_verification :
        raise HTTPException(status_code = 400, detail = "Bunday fayl mavjud")
    file_location = file.filename
    ext = os.path.splitext(file_location)[-1].lower()
    if ext not in [".jpg", ".png"] :
        raise HTTPException(status_code = 400, detail = "Yuklanayotgan fayl formatiga ruhsat berilmagan")
    with open(f"assets/galery/{file_location}", "wb+") as file_object:
        file_object.write(file.file.read())
    new_file_db = Galery(
        file = file_location,
        comment = comment,
        user_id = user.id,
        market_id = user.market_id,
    )
    db.add(new_file_db)
    db.commit()
    db.refresh(new_file_db)
    return new_file_db


def delete_galery_file(id, db) :
    galery_ver = db.query(Galery).filter(Galery.id == id).first()
    if galery_ver is None :
        raise HTTPException(status_code = 400, detail = "Bunday id raqamli fayl mavjud emas")
    db.delete(galery_ver)
    db.commit()