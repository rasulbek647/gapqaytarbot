import aiosqlite

class Database:
    def __init__(self, db_path = "config/main.db"):
        self.db_path = db_path

    async def execute(self, sql, parameters = None, fetchone=False, fetchall=False, commit=False):
        if not parameters:
            parameters = ()

        # Ma'lumotlar bazasiga ulanish
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(sql, parameters)

            data = None
            if fetchone:
                data = await cursor.fetchone()
            if fetchall:
                data = await cursor.fetchall()

            if commit:
                await db.commit()

            return data

DB = Database()
