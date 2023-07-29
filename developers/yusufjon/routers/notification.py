from fastapi import APIRouter, WebSocket, WebSocketDisconnect, WebSocketException
from databases.main import ActiveSession
from developers.yusufjon.utils.wsmanager import *
from developers.yusufjon.models.user import *
from developers.yusufjon.schemas.user import NewUser
from developers.yusufjon.schemas.notification import MessageSchema
from security.auth import jwt, SECRET_KEY, ALGORITHM

notification_router = APIRouter()


# @notification_router.get("/send_to_public")
# async def send_to_public(title: str, description: str, db: Session = ActiveSession):

#     message = MessageSchema(
#         title=title,
#         body=description,
#         imgurl="https://api2.f9.crud.uz/images/galery/niso-logo.png"
#     )

#     return await manager.send_user(message, 'plant_admin', db)


@notification_router.websocket("/connection")
async def websocket_endpoint(
    token: str,
    websocket: WebSocket,
    db: Session = ActiveSession
):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username: str = payload.get("sub")

    user: User = db.query(User).filter_by(
        username=username, disabled=False).first()

    await manager.connect(websocket, user)

    if user:

        for ntf in user.notifications:
            message = MessageSchema(
                title=ntf.title,
                body=ntf.body,
                imgurl=ntf.imgUrl,
            )
            await manager.send_personal_json(message, (websocket, user))
        db.query(Notification).filter_by(user_id=user.id).delete()
        db.commit()


    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
