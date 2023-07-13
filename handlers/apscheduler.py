import datetime

import asyncpg
from aiogram import Bot

from database.dbconnect import Request


async def check_premium(bot: Bot, pool_connect):
    request = Request(pool_connect)
    all_user = await request.select_fetch_data(table_name="users", condition="tariff = True")
    for user in all_user:
        date = datetime.datetime.now()
        date_user = user['tariff_date']
        delta = int(((date_user - date).total_seconds()) / 3600)
        if delta == 0:
            await request.update_data(table_name="users", values="tariff=False, tariff_date=NULL", condition=f"user_id={user['user_id']}")
            await bot.send_message(chat_id=user['user_id'], text='Срок действия подписки истек')
