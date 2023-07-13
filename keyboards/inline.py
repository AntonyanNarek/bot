from types import SimpleNamespace

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.callbackdata import TariffData, SupportData


def activate_tariff(button_text: SimpleNamespace) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text=button_text.activate_tariff, callback_data='call_activate_tariff')
    builder.button(text=button_text.return_menu, callback_data='return_menu')

    return builder.adjust(1).as_markup()


def return_menu(button_text: SimpleNamespace) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text=button_text.return_menu, callback_data='return_menu')

    return builder.adjust(1).as_markup()


def search_menu(button_text: SimpleNamespace) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text=button_text.example_report, callback_data='example_report')
    builder.button(text=button_text.return_menu, callback_data='return_menu')

    return builder.adjust(1).as_markup()


def create_main_menu(button_text: SimpleNamespace) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text=button_text.search_menu, callback_data='search_menu')
    builder.button(text=button_text.referral_program_menu, callback_data='referral_program')
    builder.button(text=button_text.example_report, callback_data='example_report')
    builder.button(text=button_text.support_menu, callback_data='process_get_help')
    builder.button(text=button_text.premium_menu, callback_data='call_activate_tariff')

    return builder.adjust(1).as_markup()


def get_tariff(return_btn, tariffs):
    builder = InlineKeyboardBuilder()
    for tariff in tariffs:
        builder.button(text=f'{tariff["title"]} ({tariff["price"]}₽)', callback_data=TariffData(title=tariff['title'], count=tariff['count'], price=tariff['price']))

    builder.button(text=return_btn, callback_data='return_menu')

    return builder.adjust(1).as_markup()


def get_support_panel(uid):
    builder = InlineKeyboardBuilder()

    builder.button(text='Подключится', callback_data=SupportData(user_id=uid))

    return builder.adjust(1).as_markup()
