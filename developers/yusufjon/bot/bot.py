from developers.yusufjon.bot.states import Login
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import types
from fpdf import FPDF, HTMLMixin
from . buttons import *
from developers.yusufjon.models.attandance import Attandance
from developers.yusufjon.models.user import User
from developers.yusufjon.models.bot_chat import Bot_chat
from security.auth import verify_password
from databases.main import SessionLocal
from sqlalchemy.orm import Session
from aiogram.types import InputFile
from aiogram import Dispatcher, Bot, types
from sqlalchemy import func


TOKEN = "5972947391:AAHqWpTzyHuBpplJVZ5PTBsgvkM37vpgk0k"
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
db: Session = SessionLocal()


@dp.message_handler(text="💲 Мендаги пул")
async def bot_echo(message: types.Message):
    try:

        this_user = db.query(Bot_chat).filter_by(
            chat_id=message.chat.id).filter_by(login=True).first()
        if this_user:
            user = db.query(User).filter_by(id=this_user.employee_id).first()
            await message.answer(text=f"{'{:,}'.format(user.balance)} tenge")
            
    finally:
        db.close()

    

@dp.message_handler(text="💰 Ҳисобланган маошим")
async def bot_echo(message: types.Message):
    try:

        this_user = db.query(Bot_chat).filter_by(
            chat_id=message.chat.id).filter_by(login=True).first()
        if this_user:
            user = db.query(User).filter_by(id=this_user.employee_id).first()
            await message.answer(text=f"{'{:,}'.format(user.salary)} tenge")
            
    finally:
        db.close()
    

@dp.message_handler(commands=['start'])
async def bot_echo(message: types.Message):
    await message.answer(text="Ассалому алайкум. Ҳурматли ҳодим ботдан ўзингиз ҳақигизда маълумотлар олиш учун ЛОГИН ва ПАРОЛИНГИЗ ни киритишингиз лозим.")
    await message.answer(text='Логинни киритинг ...')
    await Login.login.set()
    try:

        this_chat = db.query(Bot_chat).filter_by(
            chat_id=message.chat.id).first()
        if not this_chat:
            db.add(Bot_chat(
                chat_id=message.chat.id,
                user_id=message.from_user.id,
                username=message.from_user.username,
            ))
            db.commit()

    finally:
        db.close()


@dp.message_handler(text='❌ Чиқиш')
async def bot_echo(message: types.Message):
    await message.answer(text="Аккаунтдан чиқдингиз!", reply_markup=keyboard_login)
    try:

        db.query(Bot_chat).filter_by(chat_id=message.chat.id).update(
                {Bot_chat.login: False})
        db.commit()

    finally:
        db.close()


@dp.message_handler(text='✅ Кириш')
async def bot_echo(message: types.Message, state: FSMContext):
    await message.answer(text='Логинни киритинг ...')
    await state.reset_state()
    await Login.login.set()


@dp.message_handler(state=Login.login)
async def bot_echo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['login'] = message.text

    await Login.next()
    await message.answer(text='Паролни киритинг ...')


@dp.message_handler(state=Login.parol)
async def bot_echo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['parol'] = message.text
    state.finish()
    try:

        this_user: User = db.query(User).filter_by(
            username=data['login'], disabled=False).first()

        if not this_user:
            await message.answer("Логин ёки паролда хатолик!")
            await state.reset_state()
        else:

            if verify_password(data['parol'], this_user.passwordHash):
                await message.answer(text=f"Табриклаймиз,  {this_user.name}!", reply_markup=keyboard)
                await state.finish()

                db.query(Bot_chat).filter_by(chat_id=message.chat.id).update(
                    {Bot_chat.login: True, Bot_chat.employee_id: this_user.id, Bot_chat.date: func.now()})
                db.commit()

            else:
                await message.answer("Логин ёки паролда хатолик!!")
                await message.answer("Логинни қайта киритинг ...")
                await state.reset_state()
                await Login.login.set()

    finally:
        db.close()


class MyFPDF(FPDF, HTMLMixin):
    pass


@dp.message_handler(text="📕 Ҳисоботларни олиш")
async def bot_echo(message: types.Message):
    try:
        
        this_chat = db.query(Bot_chat).filter_by(chat_id=message.chat.id).first()

        if this_chat:
            trows = ''
            attandaces = db.query(func.sum(Attandance.wage).label("wage"), func.date(Attandance.datetime).label('datetime')).filter_by(user_id=this_chat.employee_id)\
                .order_by(Attandance.datetime.asc()).group_by(func.date(Attandance.datetime)).limit(7).all()
            for k in attandaces:
                trows +=f"<tr><td>{k.datetime}</td><td>{k.wage} tenge</td></tr>"

            pdf = MyFPDF()
            pdf.set_font_size(16)
            pdf.add_page()

            pdf.write_html(
                f"""
                <h1 align="center">Davomat</h1>
                <table border="1"><thead><tr>
                <th width="50%">Kun</th>
                <th width="50%">Maosh</th>

            </tr></thead><tbody>{trows}</tbody></table>""",
                table_line_separators=True,
            )

            pdf.output('Davomat.pdf', 'F')
            path = "Davomat.pdf"
            
            await message.answer_document(InputFile(path))

    finally:
        db.close()

