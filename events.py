from developers.yusufjon.schemas.notification import MessageSchema
from developers.yusufjon.utils.wsmanager import manager
from developers.yusufjon.models.spare_part import Spare_part
from developers.yusufjon.bot.bot import TOKEN, bot, dp
from fastapi_utils.tasks import repeat_every
from aiogram import types, Dispatcher, Bot
from databases.main import *
from sqlalchemy.orm import Session
from fastapi import APIRouter, Request, Response
from datetime import datetime, timedelta
import traceback
import os
import time

events_router = APIRouter()

db: Session = SessionLocal()

WEBHOOK_PATH = f"/bot/{TOKEN}"
WEBHOOK_URL = "https://api2.f9.crud.uz" + WEBHOOK_PATH


@events_router.on_event("startup")
async def on_startup():
    webhook_info = await bot.get_webhook_info()

    if webhook_info.url != WEBHOOK_URL:
        await bot.set_webhook(
            url=WEBHOOK_URL
        )


@events_router.on_event("startup")
@repeat_every(seconds=3, wait_first=True)
async def on_startup2():

    try:

        one_month_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        spare_parts = db.query(Spare_part).filter(Spare_part.to_date <= one_month_ago, Spare_part.reminded == False)

        if spare_parts.count() > 0:
            texts = ""
            num = 1
            for sp in spare_parts.all():
                texts = texts + f"\t{num}. {sp.machine_name}: {sp.name} \n"
                db.query(Spare_part).filter_by(id=sp.id).update({Spare_part.reminded: True})
                num += 1
            message = MessageSchema(
                title=f"Ескирган запчастлар бор.",
                body=texts,
                imgurl=f""
            )

        await manager.send_user(message, 'admin', db)
    finally:
        db.close()



@events_router.post(WEBHOOK_PATH, include_in_schema=False)
async def bot_webhook(update: dict):
    telegram_update = types.Update(**update)
    Dispatcher.set_current(dp)
    Bot.set_current(bot)
    await dp.process_update(telegram_update)

async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
  
    except Exception as e:
        error_details = traceback.format_exc().split("File")[-1]
        await bot.send_message(-1001299185219, error_details)
        # you probably want some kind of logging here
        return Response("Internal server error", status_code=500)


