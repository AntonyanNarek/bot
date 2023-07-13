import asyncio
import logging
import asyncpg

from aiogram import Bot, Dispatcher, F
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.filters import Command

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config_data.config import load_config
from handlers import users, apscheduler, apanel
from midlleware.dbmiddleware import DbSession
from database import logger
from utils.callbackdata import TariffData, SupportData
from utils.state import UserState, SupportState


async def create_pool(host, dbname, user, password):
    return await asyncpg.create_pool(user=user, password=password, database=dbname, host=host)


async def start_bot() -> None:
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s][%(levelname)s]: file = %(filename)s | func = %(funcName)s | name = %(name)s | message =  %(message)s')

    config = load_config()
    session = AiohttpSession()

    bot = Bot(token=config.bot_config.token, session=session, parse_mode='HTML')

    pool_connect = await create_pool(
        host=config.db_config.db_host,
        dbname=config.db_config.db_database,
        user=config.db_config.db_user,
        password=config.db_config.db_password
    )

    dp = Dispatcher()

    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(func=apscheduler.check_premium, trigger='cron', minute=1, kwargs={'bot': bot, 'pool_connect': pool_connect})
    scheduler.start()

    dp.update.middleware.register(DbSession(pool_connect))

    dp.message.register(users.clear_user_support, F.text == '❌ Закончить разговор')
    dp.message.register(users.clear_operator_support, F.text == '❌ Завершить разговор')
    dp.message.register(users.user_message_support, SupportState.waiting_user_state)
    dp.message.register(users.user_message_operator, SupportState.waiting_operator_state)

    dp.callback_query.register(users.operator_get_user, SupportData.filter())

    dp.message.register(users.process_start_command, Command(commands='start'))
    dp.callback_query.register(users.process_start_command, F.data == 'return_menu')
    dp.callback_query.register(users.process_search_menu, F.data == 'search_menu')
    dp.message.register(users.process_waiting_data, UserState.waiting_data_company)
    dp.callback_query.register(users.referral_program, F.data == 'referral_program')
    dp.callback_query.register(users.call_activate_tariff, F.data == 'call_activate_tariff')
    dp.callback_query.register(users.create_pay_you_kassa, TariffData.filter())
    dp.pre_checkout_query.register(users.process_pre_checkout_query)
    dp.message.register(users.payment_was_successful, F.successful_payment)
    dp.callback_query.register(users.process_get_help, F.data == 'process_get_help')
    dp.callback_query.register(users.example_report, F.data == 'example_report')
    dp.message.register(apanel.process_command_apanel, Command(commands='apanel'))
    dp.callback_query.register(apanel.free_order_status, F.data == 'free_order_status')
    dp.callback_query.register(apanel.stats_bot, F.data == 'stats_bot')
    dp.callback_query.register(users.msg_none, F.data == 'None')

    try:
        log = 'Bot successfully launched!'
        await logger.save(levelname='INFO', file='bot.py', func='start_bot', user_id='Bot', message=log)
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        log = 'The bot has completed its work!'
        await logger.save(levelname='INFO', file='bot.py', func='start_bot', user_id='Bot', message=log)


if __name__ == '__main__':
    asyncio.run(start_bot())
