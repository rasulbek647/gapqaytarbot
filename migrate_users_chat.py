import asyncio

from services.db_api.sqllite import DB


async def main():
    # users_chat jadvalini uch ustunli ko'rinishga o'tkazamiz:
    # id (AUTOINCREMENT, har bir xabar uchun alohida id)
    # user_id (foydalanuvchining Telegram ID'si)
    # chat (xabar matni)

    # Eski jadvalni vaqtincha boshqa nomga o'zgartiramiz
    await DB.execute(
        sql="ALTER TABLE users_chat RENAME TO users_chat_old;",
        commit=True,
    )

    # Yangi jadvalni yaratamiz
    await DB.execute(
        sql="""
        CREATE TABLE users_chat (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INT,
            chat VARCHAR(255)
        );
        """,
        commit=True,
    )

    # Eski ma'lumotlarni ko'chiramiz:
    # eski jadvaldagi "id" ustuni aslida user_id bo'lgani uchun shuni user_id ga yozamiz
    await DB.execute(
        sql="""
        INSERT INTO users_chat (user_id, chat)
        SELECT id AS user_id, chat FROM users_chat_old;
        """,
        commit=True,
    )

    # Eski jadvalni o'chiramiz
    await DB.execute(
        sql="DROP TABLE users_chat_old;",
        commit=True,
    )

    print("Migratsiya tugadi: users_chat jadvali yangilandi.")


if __name__ == "__main__":
    asyncio.run(main())

