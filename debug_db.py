import asyncio

from services.db_api.sqllite import DB


async def main():
    print("=== users_chat structure ===")
    table_info = await DB.execute(
        sql="PRAGMA table_info(users_chat);",
        fetchall=True,
    )
    for col in table_info or []:
        print(col)

    print("\n=== users_chat data (first 20 rows) ===")
    rows = await DB.execute(
        sql="SELECT rowid, * FROM users_chat LIMIT 20;",
        fetchall=True,
    )
    for row in rows or []:
        print(row)


if __name__ == "__main__":
    asyncio.run(main())

