from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart

from services.db_api.sqllite import DB


router = Router()


@router.message(CommandStart())
async def bot_start(message: Message):
    # O'quvchi va o'qituvchilar jadvalini (agar bo'lmasa) yaratamiz
    await DB.execute(
        sql="""
        CREATE TABLE IF NOT EXISTS persons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tg_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            full_name TEXT NOT NULL,
            age INTEGER,
            phone TEXT,
            group_name TEXT,
            subject TEXT
        );
        """,
        commit=True,
    )

    await message.answer(
        "Salom 👋\n"
        "O'quvchi va o'qituvchilarni ro'yxatdan o'tkazish uchun /register buyrug'ini yuboring.\n"
        "Agar ma'lumotlaringizni o'zgartirmoqchi bo'lsangiz, /edit buyrug'ini yuboring."
    )
