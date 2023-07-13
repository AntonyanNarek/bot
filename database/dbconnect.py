import asyncpg
from asyncpg import Record


class Request:
    def __init__(self, connector: asyncpg.pool.Pool):
        self.connector = connector

    async def insert_data(self, table_name, column, values) -> None:
        query = f"INSERT INTO {table_name} ({column}) VALUES ({values}) ON CONFLICT DO NOTHING"
        await self.connector.execute(query)
        return

    async def select_columns(self, table_name, columns, condition) -> Record:
        query = f'SELECT ({columns}) FROM {table_name} WHERE {condition}'
        return await self.connector.fetchrow(query)

    async def select_data(self, table_name, condition) -> Record:
        query = f'SELECT * FROM {table_name} WHERE {condition}'
        return await self.connector.fetchrow(query)

    async def select_full_data(self, table_name) -> Record:
        query = f'SELECT * FROM {table_name}'
        return await self.connector.fetchrow(query)

    async def select_all_fetch_data(self, table_name) -> Record:
        query = f'SELECT * FROM {table_name}'
        return await self.connector.fetch(query)

    async def select_fetch_data(self, table_name, condition) -> Record:
        query = f'SELECT * FROM {table_name} WHERE {condition}'
        return await self.connector.fetch(query)

    async def select_exists(self, table_name, condition):
        query = f'SELECT EXISTS(SELECT 1 FROM {table_name} WHERE {condition} LIMIT 1)'
        return await self.connector.fetchrow(query)

    async def update_data(self, table_name, values, condition):
        query = f'UPDATE {table_name} SET {values} WHERE {condition}'
        return await self.connector.execute(query)


    async def delete_data(self, table_name, condition):
        query = f'DELETE FROM {table_name} WHERE {condition}'
        return await self.connector.execute(query)