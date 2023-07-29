from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💲 Мендаги пул")],
        [KeyboardButton(text="💰 Ҳисобланган маошим")],
        [KeyboardButton(text="📕 Ҳисоботларни олиш")],
        [KeyboardButton(text="❌ Чиқиш")]
    ],
    resize_keyboard=True
)

keyboard_login = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="✅ Кириш")]],
    resize_keyboard=True
)
