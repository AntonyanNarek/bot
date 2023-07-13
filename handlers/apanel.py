import datetime

from aiogram.types import Message, CallbackQuery

from database.dbconnect import Request
from keyboards import inline_apanel


async def process_command_apanel(message: Message, request: Request):
    user_check = await request.select_data(table_name="users", condition=f"user_id = {message.from_user.id}")
    if user_check['admin']:
        msg = f'Добро пожаловать в панель управления'
        check_status = await request.select_columns(table_name="settings", columns="free_version", condition="id = 1")
        if check_status['free_version']:
            status = 'Вкл'
        else:
            status = 'Выкл'
        reply = inline_apanel.apanel_menu(status)
        await message.answer(text=msg, reply_markup=reply)
    else:
        return


async def free_order_status(call: CallbackQuery, request: Request):
    check_status = await request.select_columns(table_name="settings", columns="free_version", condition="id = 1")
    if check_status['free_version']:
        await request.update_data(table_name="settings", values="free_version = 'False'", condition="id = 1")
        status = 'Выкл'
    else:
        await request.update_data(table_name="settings", values="free_version = 'True'", condition="id = 1")
        status = 'Вкл'
    reply = inline_apanel.apanel_menu(status)
    await call.message.edit_reply_markup(reply_markup=reply)


async def stats_bot(call: CallbackQuery, request: Request):
    users = await request.select_all_fetch_data(table_name="users")
    users_24 = 0
    users_7 = 0
    users_30 = 0
    users_1 = 0
    users_all = len(users)
    date = datetime.datetime.now()
    for user in users:
        delta = date - user['register_date']
        if delta.days == 0:
            users_24 += 1
            users_7 += 1
            users_30 += 1
            users_1 += 1
        elif delta.days < 8:
            users_7 += 1
            users_30 += 1
            users_1 += 1
        elif delta.days < 31:
            users_30 += 1
            users_1 += 1
        elif delta.days < 366:
            users_1 += 1

    zapros = await request.select_all_fetch_data(table_name="search_stats")
    zapros_24_true = 0
    zapros_24_false = 0
    zapros_7_true = 0
    zapros_7_false = 0
    zapros_30_true = 0
    zapros_30_false = 0
    zapros_1_true = 0
    zapros_1_false = 0
    zapros_all_true = 0
    zapros_all_false = 0
    for zap in zapros:
        delta = date - zap['date']
        if delta.days == 0 and zap['result'] is True:
            zapros_24_true += 1
            zapros_7_true += 1
            zapros_30_true += 1
            zapros_1_true += 1
            zapros_all_true += 1
        elif delta.days == 0 and zap['result'] is False:
            zapros_24_false += 1
            zapros_7_false += 1
            zapros_30_false += 1
            zapros_1_false += 1
            zapros_all_false += 1
        elif delta.days < 8 and zap['result'] is True:
            zapros_7_true += 1
            zapros_30_true += 1
            zapros_1_true += 1
            zapros_all_true += 1
        elif delta.days < 8 and zap['result'] is False:
            zapros_7_false += 1
            zapros_30_false += 1
            zapros_1_false += 1
            zapros_all_false += 1
        elif delta.days < 31 and zap['result'] is True:
            zapros_30_true += 1
            zapros_1_true += 1
            zapros_all_true += 1
        elif delta.days < 31 and zap['result'] is False:
            zapros_30_false += 1
            zapros_1_false += 1
            zapros_all_false += 1
        elif delta.days < 366 and zap['result'] is True:
            zapros_1_true += 1
            zapros_all_true += 1
        elif delta.days < 366 and zap['result'] is False:
            zapros_1_false += 1
            zapros_all_false += 1
        elif delta.days > 366 and zap['result'] is True:
            zapros_all_true += 1
        else:
            zapros_all_false += 1
    pays = await request.select_all_fetch_data(table_name="stats_pay")
    pay_24 = 0
    pay_7 = 0
    pay_30 = 0
    pay_1 = 0
    pay_all = 0
    for pay in pays:
        delta = date - pay['date']
        if delta.days == 0:
            pay_24 += pay['money']
            pay_7 += pay['money']
            pay_30 += pay['money']
            pay_1 += pay['money']
            pay_all += pay['money']
        elif delta.days < 8:
            pay_7 += pay['money']
            pay_30 += pay['money']
            pay_1 += pay['money']
            pay_all += pay['money']
        elif delta.days < 31:
            pay_30 += pay['money']
            pay_1 += pay['money']
            pay_all += pay['money']
        elif delta.days < 366:
            pay_1 += pay['money']
            pay_all += pay['money']
        else:
            pay_all += pay['money']
    msg = f'Статистика пользователей:\n' \
          f'Новых за 24 часа: <b>{users_24}</b>\n' \
          f'Новых за 7 дней: <b>{users_7}</b>\n' \
          f'Новых за 30 дней: <b>{users_30}</b>\n' \
          f'Новых за год: <b>{users_1}</b>\n' \
          f'Всего пользователей: <b>{users_all}</b>\n\n' \
          f'Статистика запросов:\n' \
          f'Успешных за 24 часа: <b>{zapros_24_true}</b>\n' \
          f'Не успешных за 24 часа: <b>{zapros_24_false}</b>\n' \
          f'Успешных за 7 дней: <b>{zapros_7_true}</b>\n' \
          f'Не успешных за 7 дней: <b>{zapros_7_false}</b>\n' \
          f'Успешных за 30 дней: <b>{zapros_30_true}</b>\n' \
          f'Не успешных за 30 дней: <b>{zapros_30_false}</b>\n' \
          f'Успешных за год: <b>{zapros_1_true}</b>\n' \
          f'Не успешных за год: <b>{zapros_1_false}</b>\n' \
          f'Всего успешных: <b>{zapros_all_true}</b>\n' \
          f'Всего не успешных: <b>{zapros_all_false}</b>\n\n' \
          f'Статистика дохода:\n' \
          f'Доход за 24 часа: <b>{pay_24}₽</b>\n' \
          f'Доход за 7 дней: <b>{pay_7}₽</b>\n' \
          f'Доход за 30 дней: <b>{pay_30}₽</b>\n' \
          f'Доход за год: <b>{pay_1}₽</b>\n' \
          f'Общий доход: <b>{pay_all}₽</b>'
    await call.message.answer(text=msg)
