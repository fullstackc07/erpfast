import math
from sqlalchemy.orm import joinedload, Session
from fastapi import HTTPException
from developers.yusufjon.models.notification import *
from developers.yusufjon.schemas.notification import *

def get_all_notifications(search, page, limit, usr, db: Session):
    if page == 1 or page < 1:
        offset = 0
    else:
        offset = (page-1) * limit
    
    notifications = db.query(Notification)

    #if search:
       #notifications = notifications.filter(
           #Notification.id.like(f"%{search}%"),
       #)

    
    all_data = notifications.order_by(Notification.id.desc()).offset(offset).limit(limit)
    count_data = notifications.count()

    return {
        "data": all_data.all(),
        "page_count": math.ceil(count_data / limit),
        "data_count": count_data,
        "current_page": page,
        "page_limit": limit,
    }

def create_notification(form_data: NewNotification, usr, db: Session):
    new_notification = Notification(
        title=form_data.title,
        body=form_data.body,
        imgUrl=form_data.imgurl,
        user_id=form_data.user_id,
    )

    db.add(new_notification)
    db.commit()

    raise HTTPException(status_code=200, detail="Ma`lumotlar saqlandi!")

def update_notification(id, form_data: UpdateNotification, usr, db: Session):
    notification = db.query(Notification).filter(Notification.id == id)
    this_notification = notification.first()
    if this_notification:
        notification.update({    
            Notification.title: form_data.title,
            Notification.body: form_data.body,
            Notification.imgUrl: form_data.imgurl,
            Notification.user_id: form_data.user_id,
        })
        db.commit()

        raise HTTPException(status_code=200, detail="O`zgarish saqlandi!")
    else:
        raise HTTPException(status_code=400, detail="So`rovda xatolik!")
    
