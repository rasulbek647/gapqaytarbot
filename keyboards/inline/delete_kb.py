from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_delete_my_messages_kb() -> InlineKeyboardMarkup:
    """
    Foydalanuvchi o'z barcha xabarlarini (users_chat jadvalidan) o'chirish uchun tugma.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Mening xabarlarimni o'chirish",
                    callback_data="delete_my_messages",
                )
            ]
        ]
    )

