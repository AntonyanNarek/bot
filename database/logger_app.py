import datetime

import aiosqlite


class AsyncLogger:
    def __init__(self):
        self.db_name = '/root/project/logger.db'
        self.connection = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()

    async def connect(self):
        self.connection = await aiosqlite.connect(self.db_name)

    async def disconnect(self):
        if self.connection:
            await self.connection.close()

    async def execute(self, query, parameters=None):
        async with self.connection.execute(query, parameters) as cursor:
            return await cursor.fetchall()

    async def commit(self):
        await self.connection.commit()

    async def insert_data(self, values):
        query = f"INSERT INTO logs VALUES ({values}) ON CONFLICT DO NOTHING"
        await self.execute(query)
        await self.commit()

    async def select_data(self):
        query = f"SELECT * FROM logs"
        return await self.execute(query)


async def save(levelname, file, func, user_id, message):
    asctime = datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')
    async with AsyncLogger() as db:
        await db.insert_data(f'"{asctime}", "{levelname}", "{file}", "{func}", "{user_id}", "{message}"')


async def select():
    async with AsyncLogger() as db:
        result = await db.select_data()
    return result
