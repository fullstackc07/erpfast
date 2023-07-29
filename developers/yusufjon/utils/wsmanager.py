from fastapi import WebSocket, WebSocketException, WebSocketDisconnect
from sqlalchemy.orm import Session
from developers.yusufjon.models.user import User
from developers.yusufjon.models.notification import Notification
from developers.yusufjon.schemas.notification import MessageSchema


class ConnectionManager:

    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket, user):
        await websocket.accept()
        self.active_connections.append((websocket, user))

    def disconnect(self, websocket: WebSocket):
        for connection in self.active_connections:
            if connection[0] == websocket:
                self.active_connections.remove(connection)
                break

    async def send_personal_message(self, message: str, connection):
        websocket, user = connection
        try:
            await websocket.send_text(message)
        except WebSocketDisconnect:
            await self.disconnect(websocket)

    async def send_personal_json(self, message: MessageSchema, connection):
        websocket, user = connection
        try:
            await websocket.send_json({
                "title": message.title,
                "body": message.body,
                "imgUrl": message.imgurl,
            })

        except WebSocketDisconnect:
            await self.disconnect(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            websocket, user = connection
            try:
                await websocket.send_text(message)
            except WebSocketDisconnect:
                await self.disconnect(websocket)

    async def broadcast_json(self, message):
        for connection in self.active_connections:
            websocket, user = connection
            try: 
                await websocket.send_json(message)
            except WebSocketDisconnect:
                await self.disconnect(websocket)

    async def send_user(self, message: MessageSchema, role: str, db: Session):

        users = db.query(User.id).filter_by(role=role).all()

        sended = 0
        sended_str = ""

        for employee in users:
            sent = False
            for connection in self.active_connections:
                websocket, user = connection
                try:
                    
                    if user.id == employee.id:
                        await websocket.send_json({
                            "title": message.title,
                            "body": message.body,
                            "imgUrl": message.imgurl,
                        })
                        sent = True
                        sended += 1
                        sended_str += f"{user.username}"

                except WebSocketDisconnect:
                    await self.disconnect(websocket)

            if sent == False:
                db.add(Notification(
                    title=message.title,
                    body=message.body,
                    imgUrl=message.imgurl,
                    user_id=employee.id
                ))
                db.commit()

        return f"Message was sent to {sended} user/s, they are {sended_str}"


manager = ConnectionManager()
