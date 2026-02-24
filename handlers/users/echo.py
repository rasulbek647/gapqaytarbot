from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from services.db_api.sqllite import DB
from keyboards.inline.delete_kb import get_delete_my_messages_kb

router = Router()


@router.message(Command("delete_my"))
async def delete_my_messages_by_command(message: Message):
    """
    /delete_my <user_id>

    Masalan: /delete_my 6985557289
    users_chat jadvalidan aynan shu user_id ga tegishli barcha xabarlarni o'chiradi.
    Agar user_id ko'rsatilmasa, o'zi yozgan foydalanuvchini o'chiradi.
    """
    parts = message.text.split(maxsplit=1)

    # Agar foydalanuvchi user_id kiritgan bo'lsa – o'shani olamiz, bo'lmasa o'z user_id sini olamiz
    if len(parts) == 2 and parts[1].isdigit():
        target_user_id = int(parts[1])
    else:
        target_user_id = message.from_user.id

    await DB.execute(
        sql="DELETE FROM users_chat WHERE user_id = ?",
        parameters=(target_user_id,),
        commit=True,
    )
    await message.answer(f"user_id = {target_user_id} bo'yicha barcha xabarlar bazadan o'chirildi.")


@router.callback_query(lambda c: c.data == "delete_my_messages")
async def delete_my_messages_by_button(callback: CallbackQuery):
    """
    Tugma orqali o'chirish:
    callback_data = 'delete_my_messages' bo'lsa, shu foydalanuvchining
    users_chat dagi barcha xabarlarini user_id bo'yicha o'chiramiz.
    """
    await DB.execute(
        sql="DELETE FROM users_chat WHERE user_id = ?",
        parameters=(callback.from_user.id,),
        commit=True,
    )
    await callback.message.edit_text("Sizning barcha xabarlaringiz bazadan o'chirildi.")
    await callback.answer()


@router.message()
async def bot_echo(message: Message):
    # Oddiy xabarlarni users_chat jadvaliga yozamiz: (id, user_id, chat)
    await DB.execute(
        sql="INSERT INTO users_chat (user_id, chat) VALUES (?, ?)",
        parameters=(message.from_user.id, message.text),
        commit=True,
    )

    # Foydalanuvchiga echo + o'chirish tugmasini ko'rsatamiz
    await message.answer(
        message.text,
        reply_markup=get_delete_my_messages_kb(),
    )
