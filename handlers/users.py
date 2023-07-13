import asyncio
import datetime
from types import SimpleNamespace

from aiogram import Bot
from aiogram.types import Message, CallbackQuery, FSInputFile, LabeledPrice, PreCheckoutQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from config_data.config import load_config
from database import logger
from database.dbconnect import Request
from keyboards import inline, keyboard
from utils.callbackdata import TariffData, SupportData
from utils.format import configure_variables, MessageFormatting
from utils.HonestBusinessAPI.asyncapi import HonesBusinessClient
from utils.state import UserState, SupportState
from utils.preparation import create_doc_plus
from utils.preparation import create_doc_free


async def process_start_command(message: Message | CallbackQuery, request: Request) -> None:
    uid = message.from_user.id
    try:
        date = datetime.datetime.now()
        username = message.from_user.username
        check_user = await request.select_exists(table_name="users", condition=f"user_id = {uid}")
        if check_user['exists'] is not True:
            try:
                command = message.text.split('/start ')[1]
                arg_ = command.split('_')
                if arg_[0] == 'ref' and uid != int(arg_[1]):
                    check_ref = await request.select_exists(table_name="refferals", condition=f"ref_id = {uid}")
                    if check_ref['exists'] is not True:
                        await request.insert_data(table_name="refferals", column="user_id, ref_id, date_register", values=f"{int(arg_[1])}, {uid}, '{date}'")
                        await request.update_data(table_name="users", values="count_ref = count_ref + 1", condition=f"user_id = {int(arg_[1])}")
            except Exception:
                pass
            await request.insert_data(table_name="users", column="user_id, username, register_date", values=f"{uid}, '{username}', '{date}'")
            log = f'The user is saved in the database'
            await logger.save(levelname='INFO', file='users.py', func='process_start_command', user_id=uid, message=log)
        
        user_info = await request.select_data(table_name="users", condition=f"user_id = {uid}")
        db_setting = await request.select_data(table_name="settings", condition="id = 1")

        photo = FSInputFile('media/menu.png')

        data = configure_variables(message.from_user, user_info, db_setting)
        db_msg = await request.select_columns(table_name="message", columns="text", condition="key = 'start'")
        msg = MessageFormatting(db_msg['text'].replace('|n|', '\n'), data).message_formatting()

        db_btn_search_menu = await request.select_columns(table_name="buttons", columns="text", condition="key = 'search_menu'")
        db_btn_referral_program_menu = await request.select_columns(table_name="buttons", columns="text", condition="key = 'referral_program_menu'")
        db_btn_example_report = await request.select_columns(table_name="buttons", columns="text", condition="key = 'example_report'")
        db_btn_support_menu = await request.select_columns(table_name="buttons", columns="text", condition="key = 'support_menu'")
        db_btn_premium_menu = await request.select_columns(table_name="buttons", columns="text", condition="key = 'premium_menu'")
        data_btn = SimpleNamespace()
        data_btn.search_menu = MessageFormatting(db_btn_search_menu['text'], data).message_formatting()
        data_btn.referral_program_menu = MessageFormatting(db_btn_referral_program_menu['text'], data).message_formatting()
        data_btn.example_report = MessageFormatting(db_btn_example_report['text'], data).message_formatting()
        data_btn.support_menu = MessageFormatting(db_btn_support_menu['text'], data).message_formatting()
        data_btn.premium_menu = MessageFormatting(db_btn_premium_menu['text'], data).message_formatting()
        reply = inline.create_main_menu(data_btn)

        if isinstance(message, CallbackQuery):
            await message.message.delete()
            await message.message.answer_photo(photo=photo, caption=msg, reply_markup=reply)
        else:
            await message.answer_photo(photo=photo, caption=msg, reply_markup=reply)

    except Exception as ex:
        log = f'Exception = {ex}'
        await logger.save(levelname='ERROR', file='users.py', func='process_start_command', user_id=uid, message=log)


async def process_search_menu(call: CallbackQuery, request: Request, state: FSMContext) -> None:
    uid = call.from_user.id
    try:
        await call.message.delete()
        user_info = await request.select_data(table_name="users", condition=f"user_id = {uid}")
        db_setting = await request.select_data(table_name="settings", condition="id = 1")
        data = configure_variables(call.from_user, user_info, db_setting)
        db_msg = await request.select_columns(table_name="message", columns="text", condition="key = 'search_menu'")
        msg = MessageFormatting(db_msg['text'].replace('|n|', '\n'), data).message_formatting()

        db_btn_example_report = await request.select_columns(table_name="buttons", columns="text", condition="key = 'example_report'")
        db_btn_return_menu = await request.select_columns(table_name="buttons", columns="text", condition="key = 'return_menu'")

        data_btn = SimpleNamespace()
        data_btn.example_report = MessageFormatting(db_btn_example_report['text'], data).message_formatting()
        data_btn.return_menu = MessageFormatting(db_btn_return_menu['text'], data).message_formatting()
        reply = inline.search_menu(data_btn)

        await call.message.answer(text=msg, reply_markup=reply)
        await state.set_state(UserState.waiting_data_company)
    except Exception as ex:
        log = f'Exception = {ex}'
        await logger.save(levelname='ERROR', file='users.py', func='process_search_menu', user_id=uid, message=log)


async def process_waiting_data(message: Message, request: Request, state: FSMContext, bot: Bot) -> None:
    uid = message.from_user.id
    msg_stick = await message.answer_sticker(sticker='CAACAgEAAxkBAAEJL3BkeaFD14YtKP0tWTZpUuizzZ-x9QACRgMAAiqHGURoXzCXdu7QsS8E')
    try:
        settings_load = await request.select_full_data(table_name='settings')
        if settings_load['free_version'] is not True:
            user_info = await request.select_data(table_name="users", condition=f"user_id = {uid}")
            db_setting = await request.select_data(table_name="settings", condition="id = 1")
            data = configure_variables(message.from_user, user_info, db_setting)
            db_msg = await request.select_columns(table_name="message", columns="text", condition="key = 'error_free_version'")
            msg = MessageFormatting(db_msg['text'].replace('|n|', '\n'), data).message_formatting()

            db_btn_activate_tariff = await request.select_columns(table_name="buttons", columns="text", condition="key = 'activate_tariff'")
            db_btn_return_menu = await request.select_columns(table_name="buttons", columns="text", condition="key = 'return_menu'")
            data_btn = SimpleNamespace()
            data_btn.activate_tariff = MessageFormatting(db_btn_activate_tariff['text'], data).message_formatting()
            data_btn.return_menu = MessageFormatting(db_btn_return_menu['text'], data).message_formatting()
            reply = inline.activate_tariff(data_btn)

            await message.answer(text=msg, reply_markup=reply)

            log = f'User does not have an activated tariff'
            await logger.save(levelname='WARNING', file='users.py', func='process_waiting_data', user_id=uid, message=log)
            return

        user_tariff = await request.select_columns(table_name="users", columns="tariff", condition=f"user_id = {uid}")

        if user_tariff['tariff']:
            client = HonesBusinessClient()
            card = await client.card(message.text)
            if card.get('body').get('docs') is not None:
                card_ = card.get('body').get('docs', [])[0]
            else:
                card_ = card.get('body')

            try:
                ogrn = card_.get('ОГРН')
            except AttributeError:
                await bot.delete_message(chat_id=msg_stick.chat.id, message_id=msg_stick.message_id)
                user_info = await request.select_data(table_name="users", condition=f"user_id = {uid}")
                db_setting = await request.select_data(table_name="settings", condition="id = 1")
                data = configure_variables(message.from_user, user_info, db_setting)
                db_btn_return_menu = await request.select_columns(table_name="buttons", columns="text", condition="key = 'return_menu'")
                data_btn = SimpleNamespace()
                data_btn.return_menu = MessageFormatting(db_btn_return_menu['text'], data).message_formatting()
                reply = inline.return_menu(data_btn)
                msg_db = await request.select_columns(table_name="message", columns="text", condition="key = 'error_search'")
                msg = MessageFormatting(msg_db['text'], data).message_formatting()
                await message.answer(text=msg, reply_markup=reply)
                await state.clear()
                date = datetime.datetime.now()
                await request.insert_data(table_name="search_stats", column="user_id, result, date", values=f"{uid}, 'False', '{date}'")
                return

            inn = card_.get('ИНН')
            fns_card = await client.fns_card(ogrn)
            affilation_company = await client.affilation_company(ogrn)
            court_arbitration = await client.court_arbitration(ogrn)
            zakupki_top = await client.zakupki_top(inn)
            fssp_list = await client.fssp_list(ogrn)
            proverki = await client.proverki(ogrn)
            licenses = await client.licenses(ogrn)
            important_facts = await client.important_facts(ogrn)
            path = create_doc_plus.create_pdf_doc(card_, fns_card, affilation_company, court_arbitration, zakupki_top, fssp_list, proverki, licenses, important_facts)
            path = FSInputFile(path=path)
            await bot.delete_message(chat_id=msg_stick.chat.id, message_id=msg_stick.message_id)
            user_info = await request.select_data(table_name="users", condition=f"user_id = {uid}")
            db_setting = await request.select_data(table_name="settings", condition="id = 1")
            data = configure_variables(message.from_user, user_info, db_setting)
            db_btn_return_menu = await request.select_columns(table_name="buttons", columns="text", condition="key = 'return_menu'")
            data_btn = SimpleNamespace()
            data_btn.return_menu = MessageFormatting(db_btn_return_menu['text'], data).message_formatting()
            reply = inline.return_menu(data_btn)
            msg_db = await request.select_columns(table_name="message", columns="text", condition="key = 'search_good_plus'")
            msg = MessageFormatting(msg_db['text'], data).message_formatting()
            await message.answer_document(document=path, caption=msg, reply_markup=reply)
            await state.clear()
            date = datetime.datetime.now()
            await request.insert_data(table_name="search_stats", column="user_id, result, date", values=f"{uid}, 'True', '{date}'")
        else:
            client = HonesBusinessClient()
            card = await client.card(message.text)
            if card.get('body').get('docs') is not None:
                card_ = card.get('body').get('docs')[0]
            else:
                card_ = card.get('body')

            try:
                ogrn = card_.get('ОГРН')

            except AttributeError:
                await bot.delete_message(chat_id=msg_stick.chat.id, message_id=msg_stick.message_id)
                user_info = await request.select_data(table_name="users", condition=f"user_id = {uid}")
                db_setting = await request.select_data(table_name="settings", condition="id = 1")
                data = configure_variables(message.from_user, user_info, db_setting)
                db_btn_return_menu = await request.select_columns(table_name="buttons", columns="text", condition="key = 'return_menu'")
                data_btn = SimpleNamespace()
                data_btn.return_menu = MessageFormatting(db_btn_return_menu['text'], data).message_formatting()
                reply = inline.return_menu(data_btn)
                msg_db = await request.select_columns(table_name="message", columns="text", condition="key = 'error_search'")
                msg = MessageFormatting(msg_db['text'], data).message_formatting()
                await message.answer(text=msg, reply_markup=reply)
                await state.clear()
                date = datetime.datetime.now()
                await request.insert_data(table_name="search_stats", column="user_id, result, date", values=f"{uid}, 'False', '{date}'")
                return

            inn = card_.get('ИНН')
            fns_card = await client.fns_card(ogrn)
            await asyncio.sleep(2)
            proverki = await client.proverki(ogrn)
            await asyncio.sleep(2)
            court_arbitration = await client.court_arbitration(ogrn)
            await asyncio.sleep(2)
            zakupki_top = await client.zakupki_top(inn)
            await asyncio.sleep(2)
            fssp_list = await client.fssp_list(ogrn)
            path = create_doc_free.create_pdf_doc_free(card_, fns_card, proverki, court_arbitration, zakupki_top, fssp_list)
            path = FSInputFile(path=path)
            await bot.delete_message(chat_id=msg_stick.chat.id, message_id=msg_stick.message_id)
            user_info = await request.select_data(table_name="users", condition=f"user_id = {uid}")
            db_setting = await request.select_data(table_name="settings", condition="id = 1")
            data = configure_variables(message.from_user, user_info, db_setting)
            db_btn_activate_tariff = await request.select_columns(table_name="buttons", columns="text", condition="key = 'activate_tariff'")
            db_btn_return_menu = await request.select_columns(table_name="buttons", columns="text", condition="key = 'return_menu'")
            data_btn = SimpleNamespace()
            data_btn.activate_tariff = MessageFormatting(db_btn_activate_tariff['text'], data).message_formatting()
            data_btn.return_menu = MessageFormatting(db_btn_return_menu['text'], data).message_formatting()
            reply = inline.activate_tariff(data_btn)
            msg_db = await request.select_columns(table_name="message", columns="text", condition="key = 'search_good_free'")
            msg = MessageFormatting(msg_db['text'], data).message_formatting()
            await message.answer_document(document=path, caption=msg, reply_markup=reply)
            date = datetime.datetime.now()
            await request.insert_data(table_name="search_stats", column="user_id, result, date", values=f"{uid}, 'True', '{date}'")
            await state.clear()
    except Exception as ex:
        await bot.delete_message(chat_id=msg_stick.chat.id, message_id=msg_stick.message_id)
        log = f'Exception = {ex}'
        await logger.save(levelname='ERROR', file='users.py', func='process_waiting_data', user_id=uid, message=log)
        user_info = await request.select_data(table_name="users", condition=f"user_id = {uid}")
        db_setting = await request.select_data(table_name="settings", condition="id = 1")
        data = configure_variables(message.from_user, user_info, db_setting)
        db_btn_return_menu = await request.select_columns(table_name="buttons", columns="text", condition="key = 'return_menu'")
        data_btn = SimpleNamespace()
        data_btn.return_menu = MessageFormatting(db_btn_return_menu['text'], data).message_formatting()
        reply = inline.return_menu(data_btn)
        msg_db = await request.select_columns(table_name="message", columns="text", condition="key = 'error_search'")
        msg = MessageFormatting(msg_db['text'], data).message_formatting()
        await message.answer(text=msg, reply_markup=reply)
        date = datetime.datetime.now()
        await request.insert_data(table_name="search_stats", column="user_id, result, date", values=f"{uid}, 'False', '{date}'")
    finally:
        await state.clear()


async def referral_program(call: CallbackQuery, request: Request):
    await call.message.delete()
    uid = call.from_user.id
    try:
        db_msg = await request.select_columns(table_name="message", columns="text", condition="key = 'referral_program'")
        user_info = await request.select_data(table_name="users", condition=f"user_id = {uid}")
        db_setting = await request.select_data(table_name="settings", condition="id = 1")
        data = configure_variables(call.from_user, user_info, db_setting)
        msg = MessageFormatting(db_msg['text'].replace('|n|', '\n'), data).message_formatting()
        db_btn_return_menu = await request.select_columns(table_name="buttons", columns="text", condition="key = 'return_menu'")
        data_btn = SimpleNamespace()
        data_btn.return_menu = MessageFormatting(db_btn_return_menu['text'], data).message_formatting()
        reply = inline.return_menu(data_btn)
        await call.message.answer(text=msg, reply_markup=reply)
    except Exception as ex:
        log = f'Exception = {ex}'
        await logger.save(levelname='ERROR', file='users.py', func='referral_program', user_id=uid, message=log)


async def process_get_help(call: CallbackQuery, request: Request, state: FSMContext, bot: Bot):
    uid = call.from_user.id
    await call.message.delete()
    await request.insert_data(table_name="support", column="user_id", values=f"{uid}")
    db_msg = await request.select_columns(table_name="message", columns="text", condition="key = 'get_help'")
    user_info = await request.select_data(table_name="users", condition=f"user_id = {uid}")
    db_setting = await request.select_data(table_name="settings", condition="id = 1")
    data = configure_variables(call.from_user, user_info, db_setting)
    msg = MessageFormatting(db_msg['text'].replace('|n|', '\n'), data).message_formatting()
    reply = keyboard.support()
    await call.message.answer(text=msg, reply_markup=reply)
    await state.set_state(SupportState.waiting_user_state)

    # Сообщение администратору
    msg_db = await request.select_columns(table_name="message", columns="text", condition="key = 'new_support_admin'")
    msg = MessageFormatting(msg_db['text'].replace('|n|', '\n'), data).message_formatting()
    reply = inline.get_support_panel(uid)
    admins = await request.select_fetch_data(table_name="users", condition="admin = True")
    for admin in admins:
        try:
            await bot.send_message(chat_id=admin['user_id'], text=msg, reply_markup=reply)
        except Exception:
            continue


async def user_message_support(message: Message, request: Request, bot: Bot, state: FSMContext):
    uid = message.from_user.id
    check_support = await request.select_columns(table_name="support", columns="support_id", condition=f"user_id = {uid}")
    user_info = await request.select_data(table_name="users", condition=f"user_id = {uid}")
    db_setting = await request.select_data(table_name="settings", condition="id = 1")
    data = configure_variables(message.from_user, user_info, db_setting)
    if check_support is None:
        db_msg = await request.select_columns(table_name="message", columns="text", condition="key = 'support_finish'")
        msg = MessageFormatting(db_msg['text'].replace('|n|', '\n'), data).message_formatting()
        await message.answer(text=msg, reply_markup=ReplyKeyboardRemove())
        user_info = await request.select_data(table_name="users", condition=f"user_id = {uid}")
        db_setting = await request.select_data(table_name="settings", condition="id = 1")
        data = configure_variables(message.from_user, user_info, db_setting)
        photo = FSInputFile('media/menu.png')
        db_msg = await request.select_columns(table_name="message", columns="text", condition="key = 'start'")
        msg = MessageFormatting(db_msg['text'].replace('|n|', '\n'), data).message_formatting()
        db_btn_search_menu = await request.select_columns(table_name="buttons", columns="text", condition="key = 'search_menu'")
        db_btn_referral_program_menu = await request.select_columns(table_name="buttons", columns="text", condition="key = 'referral_program_menu'")
        db_btn_example_report = await request.select_columns(table_name="buttons", columns="text", condition="key = 'example_report'")
        db_btn_support_menu = await request.select_columns(table_name="buttons", columns="text", condition="key = 'support_menu'")
        db_btn_premium_menu = await request.select_columns(table_name="buttons", columns="text", condition="key = 'premium_menu'")
        data_btn = SimpleNamespace()
        data_btn.search_menu = MessageFormatting(db_btn_search_menu['text'], data).message_formatting()
        data_btn.referral_program_menu = MessageFormatting(db_btn_referral_program_menu['text'], data).message_formatting()
        data_btn.example_report = MessageFormatting(db_btn_example_report['text'], data).message_formatting()
        data_btn.support_menu = MessageFormatting(db_btn_support_menu['text'], data).message_formatting()
        data_btn.premium_menu = MessageFormatting(db_btn_premium_menu['text'], data).message_formatting()
        reply = inline.create_main_menu(data_btn)
        await message.answer_photo(photo=photo, caption=msg, reply_markup=reply)
        await state.clear()
    elif check_support['support_id'] is None:
        msg_db = await request.select_columns(table_name="message", columns="text", condition="key = 'support_waiting'")
        msg = MessageFormatting(msg_db['text'].replace('|n|', '\n'), data).message_formatting()
        await message.answer(text=msg)
    else:
        msg_db = await request.select_columns(table_name="message", columns="text", condition="key = 'support_user_msg'")
        msg = MessageFormatting(msg_db['text'].replace('|n|', '\n'), data).message_formatting()
        await bot.send_message(chat_id=check_support['support_id'], text=msg)
        await bot.copy_message(chat_id=check_support['support_id'], from_chat_id=uid, message_id=message.message_id)


async def operator_get_user(call: CallbackQuery, state: FSMContext, request: Request, callback_data: SupportData, bot: Bot):
    uid = call.from_user.id
    check_support = await request.select_columns(table_name="support", columns="support_id", condition=f"user_id = {callback_data.user_id}")
    user_info = await request.select_data(table_name="users", condition=f"user_id = {uid}")
    db_setting = await request.select_data(table_name="settings", condition="id = 1")
    data = configure_variables(call.from_user, user_info, db_setting)
    if check_support is None:
        msg_db = await request.select_columns(table_name="message", columns="text", condition="key = 'support_dialog_none'")
        msg = MessageFormatting(msg_db['text'].replace('|n|', '\n'), data).message_formatting()
        await call.answer(text=msg, show_alert=True)
        await call.message.delete()
        return
    elif check_support['support_id'] is not None:
        msg_db = await request.select_columns(table_name="message", columns="text", condition="key = 'support_operator_another'")
        msg = MessageFormatting(msg_db['text'].replace('|n|', '\n'), data).message_formatting()
        await call.answer(text=msg, show_alert=True)
        await call.message.delete()
        return
    elif callback_data.user_id == call.from_user.id:
        msg_db = await request.select_columns(table_name="message", columns="text", condition="key = 'support_my_help'")
        msg = MessageFormatting(msg_db['text'].replace('|n|', '\n'), data).message_formatting()
        await call.answer(text=msg, show_alert=True)
        await call.message.delete()
        return
    try:
        await request.update_data(table_name="support", values=f"support_id = {call.from_user.id}", condition=f"user_id = {callback_data.user_id}")
    except Exception:
        msg_db = await request.select_columns(table_name="message", columns="text", condition="key = 'support_msg_two'")
        msg = MessageFormatting(msg_db['text'].replace('|n|', '\n'), data).message_formatting()
        await call.answer(text=msg, show_alert=True)
        return
    await call.message.delete()
    msg_db = await request.select_columns(table_name="message", columns="text", condition="key = 'support_operator_connect'")
    msg = MessageFormatting(msg_db['text'].replace('|n|', '\n'), data).message_formatting()
    await bot.send_message(chat_id=callback_data.user_id, text=msg)
    msg_db = await request.select_columns(table_name="message", columns="text", condition="key = 'support_you_connect'")
    msg = MessageFormatting(msg_db['text'].replace('|n|', '\n'), data).message_formatting()
    reply = keyboard.support_operator()
    await call.message.answer(text=msg, reply_markup=reply)
    await state.set_state(SupportState.waiting_operator_state)


async def user_message_operator(message: Message, request: Request, bot: Bot, state: FSMContext):
    uid = message.from_user.id
    check_support = await request.select_columns(table_name="support", columns="user_id", condition=f"support_id = {uid}")
    user_info = await request.select_data(table_name="users", condition=f"user_id = {uid}")
    db_setting = await request.select_data(table_name="settings", condition="id = 1")
    data = configure_variables(message.from_user, user_info, db_setting)
    if check_support is None:
        msg_db = await request.select_columns(table_name="message", columns="text", condition="key = 'support_dialog_none'")
        msg = MessageFormatting(msg_db['text'].replace('|n|', '\n'), data).message_formatting()
        await message.answer(text=msg, reply_markup=ReplyKeyboardRemove())
        user_info = await request.select_data(table_name="users", condition=f"user_id = {uid}")
        db_setting = await request.select_data(table_name="settings", condition="id = 1")
        data = configure_variables(message.from_user, user_info, db_setting)
        photo = FSInputFile('media/menu.png')
        db_msg = await request.select_columns(table_name="message", columns="text", condition="key = 'start'")
        msg = MessageFormatting(db_msg['text'].replace('|n|', '\n'), data).message_formatting()
        db_btn_search_menu = await request.select_columns(table_name="buttons", columns="text", condition="key = 'search_menu'")
        db_btn_referral_program_menu = await request.select_columns(table_name="buttons", columns="text", condition="key = 'referral_program_menu'")
        db_btn_example_report = await request.select_columns(table_name="buttons", columns="text", condition="key = 'example_report'")
        db_btn_support_menu = await request.select_columns(table_name="buttons", columns="text", condition="key = 'support_menu'")
        db_btn_premium_menu = await request.select_columns(table_name="buttons", columns="text", condition="key = 'premium_menu'")
        data_btn = SimpleNamespace()
        data_btn.search_menu = MessageFormatting(db_btn_search_menu['text'], data).message_formatting()
        data_btn.referral_program_menu = MessageFormatting(db_btn_referral_program_menu['text'], data).message_formatting()
        data_btn.example_report = MessageFormatting(db_btn_example_report['text'], data).message_formatting()
        data_btn.support_menu = MessageFormatting(db_btn_support_menu['text'], data).message_formatting()
        data_btn.premium_menu = MessageFormatting(db_btn_premium_menu['text'], data).message_formatting()
        reply = inline.create_main_menu(data_btn)
        await message.answer_photo(photo=photo, caption=msg, reply_markup=reply)
        await state.clear()
    else:
        msg_db = await request.select_columns(table_name="message", columns="text", condition="key = 'support_operator_msg'")
        msg = MessageFormatting(msg_db['text'].replace('|n|', '\n'), data).message_formatting()
        await bot.send_message(chat_id=check_support['user_id'], text=msg)
        await bot.copy_message(chat_id=check_support['user_id'], from_chat_id=uid, message_id=message.message_id)


async def clear_operator_support(message: Message, request: Request, state: FSMContext, bot: Bot):
    await state.clear()
    uid = message.from_user.id
    check_support = await request.select_columns(table_name="support", columns="user_id", condition=f"support_id = {uid}")
    user_info = await request.select_data(table_name="users", condition=f"user_id = {uid}")
    db_setting = await request.select_data(table_name="settings", condition="id = 1")
    data = configure_variables(message.from_user, user_info, db_setting)
    if check_support is None:
        msg_db = await request.select_columns(table_name="message", columns="text", condition="key = 'support_dialog_none'")
        msg = MessageFormatting(msg_db['text'].replace('|n|', '\n'), data).message_formatting()
        await message.answer(text=msg, reply_markup=ReplyKeyboardRemove())
        await state.clear()
        photo = FSInputFile('media/menu.png')
        db_msg = await request.select_columns(table_name="message", columns="text", condition="key = 'start'")
        msg = MessageFormatting(db_msg['text'].replace('|n|', '\n'), data).message_formatting()
        db_btn_search_menu = await request.select_columns(table_name="buttons", columns="text", condition="key = 'search_menu'")
        db_btn_referral_program_menu = await request.select_columns(table_name="buttons", columns="text", condition="key = 'referral_program_menu'")
        db_btn_example_report = await request.select_columns(table_name="buttons", columns="text", condition="key = 'example_report'")
        db_btn_support_menu = await request.select_columns(table_name="buttons", columns="text", condition="key = 'support_menu'")
        db_btn_premium_menu = await request.select_columns(table_name="buttons", columns="text", condition="key = 'premium_menu'")
        data_btn = SimpleNamespace()
        data_btn.search_menu = MessageFormatting(db_btn_search_menu['text'], data).message_formatting()
        data_btn.referral_program_menu = MessageFormatting(db_btn_referral_program_menu['text'], data).message_formatting()
        data_btn.example_report = MessageFormatting(db_btn_example_report['text'], data).message_formatting()
        data_btn.support_menu = MessageFormatting(db_btn_support_menu['text'], data).message_formatting()
        data_btn.premium_menu = MessageFormatting(db_btn_premium_menu['text'], data).message_formatting()
        reply = inline.create_main_menu(data_btn)
        await message.answer_photo(photo=photo, caption=msg, reply_markup=reply)
        return
    db_msg = await request.select_columns(table_name="message", columns="text", condition="key = 'clear_support_operator'")
    msg = MessageFormatting(db_msg['text'].replace('|n|', '\n'), data).message_formatting()
    await bot.send_message(chat_id=check_support['user_id'], text=msg)
    await request.delete_data(table_name="support", condition=f"support_id = {uid}")
    msg_db = await request.select_columns(table_name="message", columns="text", condition="key = 'support_operator_disconnect'")
    msg = MessageFormatting(msg_db['text'].replace('|n|', '\n'), data).message_formatting()
    await message.answer(text=msg, reply_markup=ReplyKeyboardRemove())

    photo = FSInputFile('media/menu.png')
    db_msg = await request.select_columns(table_name="message", columns="text", condition="key = 'start'")
    msg = MessageFormatting(db_msg['text'].replace('|n|', '\n'), data).message_formatting()
    db_btn_search_menu = await request.select_columns(table_name="buttons", columns="text", condition="key = 'search_menu'")
    db_btn_referral_program_menu = await request.select_columns(table_name="buttons", columns="text", condition="key = 'referral_program_menu'")
    db_btn_example_report = await request.select_columns(table_name="buttons", columns="text", condition="key = 'example_report'")
    db_btn_support_menu = await request.select_columns(table_name="buttons", columns="text", condition="key = 'support_menu'")
    db_btn_premium_menu = await request.select_columns(table_name="buttons", columns="text", condition="key = 'premium_menu'")
    data_btn = SimpleNamespace()
    data_btn.search_menu = MessageFormatting(db_btn_search_menu['text'], data).message_formatting()
    data_btn.referral_program_menu = MessageFormatting(db_btn_referral_program_menu['text'], data).message_formatting()
    data_btn.example_report = MessageFormatting(db_btn_example_report['text'], data).message_formatting()
    data_btn.support_menu = MessageFormatting(db_btn_support_menu['text'], data).message_formatting()
    data_btn.premium_menu = MessageFormatting(db_btn_premium_menu['text'], data).message_formatting()
    reply = inline.create_main_menu(data_btn)
    await message.answer_photo(photo=photo, caption=msg, reply_markup=reply)


async def clear_user_support(message: Message, request: Request, state: FSMContext, bot: Bot):
    await state.clear()
    uid = message.from_user.id
    check_support = await request.select_columns(table_name="support", columns="support_id", condition=f"user_id = {uid}")
    user_info = await request.select_data(table_name="users", condition=f"user_id = {uid}")
    db_setting = await request.select_data(table_name="settings", condition="id = 1")
    data = configure_variables(message.from_user, user_info, db_setting)
    try:
        msg_db = await request.select_columns(table_name="message", columns="text", condition="key = 'support_user_disconnect'")
        msg = MessageFormatting(msg_db['text'].replace('|n|', '\n'), data).message_formatting()
        await bot.send_message(chat_id=check_support['support_id'], text=msg)
    except Exception:
        pass
    user_info = await request.select_data(table_name="users", condition=f"user_id = {uid}")
    db_setting = await request.select_data(table_name="settings", condition="id = 1")
    data = configure_variables(message.from_user, user_info, db_setting)

    db_msg = await request.select_columns(table_name="message", columns="text", condition="key = 'clear_support_user'")
    msg = MessageFormatting(db_msg['text'].replace('|n|', '\n'), data).message_formatting()
    await message.answer(text=msg, reply_markup=ReplyKeyboardRemove())
    await request.delete_data(table_name="support", condition=f"user_id = {uid}")

    photo = FSInputFile('media/menu.png')
    db_msg = await request.select_columns(table_name="message", columns="text", condition="key = 'start'")
    msg = MessageFormatting(db_msg['text'].replace('|n|', '\n'), data).message_formatting()
    db_btn_search_menu = await request.select_columns(table_name="buttons", columns="text", condition="key = 'search_menu'")
    db_btn_referral_program_menu = await request.select_columns(table_name="buttons", columns="text", condition="key = 'referral_program_menu'")
    db_btn_example_report = await request.select_columns(table_name="buttons", columns="text", condition="key = 'example_report'")
    db_btn_support_menu = await request.select_columns(table_name="buttons", columns="text", condition="key = 'support_menu'")
    db_btn_premium_menu = await request.select_columns(table_name="buttons", columns="text", condition="key = 'premium_menu'")
    data_btn = SimpleNamespace()
    data_btn.search_menu = MessageFormatting(db_btn_search_menu['text'], data).message_formatting()
    data_btn.referral_program_menu = MessageFormatting(db_btn_referral_program_menu['text'], data).message_formatting()
    data_btn.example_report = MessageFormatting(db_btn_example_report['text'], data).message_formatting()
    data_btn.support_menu = MessageFormatting(db_btn_support_menu['text'], data).message_formatting()
    data_btn.premium_menu = MessageFormatting(db_btn_premium_menu['text'], data).message_formatting()
    reply = inline.create_main_menu(data_btn)
    await message.answer_photo(photo=photo, caption=msg, reply_markup=reply)


async def call_activate_tariff(call: CallbackQuery, request: Request):
    uid = call.from_user.id
    try:
        await call.message.delete()
        user_info = await request.select_data(table_name="users", condition=f"user_id = {uid}")
        db_setting = await request.select_data(table_name="settings", condition="id = 1")
        data = configure_variables(call.from_user, user_info, db_setting)
        db_msg = await request.select_columns(table_name="message", columns="text", condition="key = 'activate_tariff'")
        msg = MessageFormatting(db_msg['text'].replace('|n|', '\n'), data).message_formatting()
        tariff = await request.select_all_fetch_data(table_name="tariff")
        db_btn_return_menu = await request.select_columns(table_name="buttons", columns="text", condition="key = 'return_menu'")
        btn_return_menu = MessageFormatting(db_btn_return_menu['text'], data).message_formatting()
        reply = inline.get_tariff(btn_return_menu, tariff)
        await call.message.answer(text=msg, reply_markup=reply)
    except Exception as ex:
        log = f'Exception = {ex}'
        await logger.save(levelname='ERROR', file='users.py', func='call_activate_tariff', user_id=uid, message=log)


async def create_pay_you_kassa(call: CallbackQuery, callback_data: TariffData, bot: Bot, request: Request):
    uid = call.from_user.id
    try:
        await call.message.delete()
        user_info = await request.select_data(table_name="users", condition=f"user_id = {uid}")
        if user_info['money'] < callback_data.price:
            config = load_config()
            await bot.send_invoice(
                chat_id=call.from_user.id,
                title=callback_data.title,
                description='Оплата платной подписки в боте: Бот проверки контрагентов',
                payload=f'data_{callback_data.count}',
                provider_token=config.api_pay.you_kassa,
                currency='rub',
                prices=[LabeledPrice(label=callback_data.title, amount=(callback_data.price * 100))],
                start_parameter='time-machine-example'
            )
        else:
            day = callback_data.count / 24
            db_tariff = await request.select_columns(table_name="users", columns="tariff_date", condition=f"user_id = {uid}")
            if db_tariff['tariff_date'] is not None:
                delta_db = db_tariff['tariff_date'] - datetime.datetime.now()
                day += delta_db.days
            tariff_date = datetime.datetime.now() + datetime.timedelta(days=day)
            await request.update_data(table_name="users", values=f"tariff_date = '{tariff_date}', money = money- {callback_data.price}, tariff=True", condition=f"user_id = {uid}")
            user_info = await request.select_data(table_name="users", condition=f"user_id = {uid}")
            db_setting = await request.select_data(table_name="settings", condition="id = 1")
            data = configure_variables(call.from_user, user_info, db_setting)
            db_msg = await request.select_columns(table_name="message", columns="text", condition="key = 'tariff_successful'")
            msg = MessageFormatting(db_msg['text'].replace('|n|', '\n'), data).message_formatting()
            db_btn_return_menu = await request.select_columns(table_name="buttons", columns="text", condition="key = 'return_menu'")
            data_btn = SimpleNamespace()
            data_btn.return_menu = MessageFormatting(db_btn_return_menu['text'], data).message_formatting()
            reply = inline.return_menu(data_btn)
            await call.message.answer(text=msg, reply_markup=reply)
    except Exception as ex:
        log = f'Exception = {ex}'
        await logger.save(levelname='ERROR', file='users.py', func='create_pay_you_kassa', user_id=uid, message=log)


async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


async def payment_was_successful(message: Message, request: Request):
    uid = message.from_user.id
    try:
        ref = await request.select_columns(table_name="refferals", columns="user_id", condition=f"ref_id = {uid}")
        db_setting = await request.select_data(table_name="settings", condition="id = 1")
        if ref is not None:
            ref_money = int(((message.successful_payment.total_amount / 100) * db_setting['ref_perc']) / 100)
            await request.update_data(table_name="users", values=f"money = money + {ref_money}, money_ref = money_ref + {ref_money}", condition=f"user_id = {ref['user_id']}")
        count = int(message.successful_payment.invoice_payload.split('data_')[1])
        day = int(count / 24)
        money = int(message.successful_payment.total_amount / 100)
        db_tariff = await request.select_columns(table_name="users", columns="tariff_date", condition=f"user_id = {uid}")
        if db_tariff['tariff_date'] is not None:
            delta_db = db_tariff['tariff_date'] - datetime.datetime.now()
            day += delta_db.days
        tariff_date = datetime.datetime.now() + datetime.timedelta(days=day)
        await request.update_data(table_name="users", values=f"tariff_date = '{tariff_date}', tariff=True", condition=f"user_id = {uid}")
        date = datetime.datetime.now()
        await request.insert_data(table_name="stats_pay", column="user_id, money, date", values=f"{uid}, {money}, '{date}'")
        user_info = await request.select_data(table_name="users", condition=f"user_id = {uid}")
        data = configure_variables(message.from_user, user_info, db_setting)
        db_msg = await request.select_columns(table_name="message", columns="text", condition="key = 'tariff_successful'")
        msg = MessageFormatting(db_msg['text'].replace('|n|', '\n'), data).message_formatting()
        db_btn_return_menu = await request.select_columns(table_name="buttons", columns="text", condition="key = 'return_menu'")
        data_btn = SimpleNamespace()
        data_btn.return_menu = MessageFormatting(db_btn_return_menu['text'], data).message_formatting()
        reply = inline.return_menu(data_btn)
        await message.answer(text=msg, reply_markup=reply)
    except Exception as ex:
        log = f'Exception = {ex}'
        await logger.save(levelname='ERROR', file='users.py', func='payment_was_successful', user_id=uid, message=log)


async def example_report(call: CallbackQuery):
    doc = FSInputFile('media/ООО Яндекс.pdf')
    await call.message.answer_document(document=doc)


async def msg_none(call: CallbackQuery) -> None:
    await call.answer(text='В разработке')
