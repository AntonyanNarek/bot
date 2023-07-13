import datetime
from types import SimpleNamespace

from aiogram.types import User
from asyncpg import Record


class MessageFormatting:
    """
    Класс для форматирования сообщений
    """

    def __init__(self, text: str, values: SimpleNamespace):
        self.text = text

        self.user_id = values.user_id
        self.first_name = values.first_name
        self.username = values.username
        self.bot_id = values.bot_id
        self.money = values.money
        self.count_ref = values.count_ref
        self.money_ref = values.money_ref
        self.ref_perc = values.ref_perc
        self.tariff_date = values.tariff_date

    def message_formatting(self) -> str:
        return self.text.format(
            user_id=self.user_id,
            first_name=self.first_name,
            username=self.username,
            bot_id=self.bot_id,
            money=self.money,
            count_ref=self.count_ref,
            money_ref=self.money_ref,
            ref_perc=self.ref_perc,
            tariff_date=self.tariff_date
        )


def configure_variables(from_user: User, db_data: Record, db_setting: Record) -> SimpleNamespace:
    """
    Функция присвоения значений.
    Возвращает объект класса SimpleNamespace
    :return:
    """
    data = SimpleNamespace()

    data.user_id = from_user.id
    data.first_name = from_user.first_name
    data.username = from_user.username
    data.bot_id = db_data['id']
    data.money = db_data['money']
    data.count_ref = db_data['count_ref']
    data.money_ref = db_data['money_ref']
    data.ref_perc = db_setting['ref_perc']
    if db_data['tariff_date'] is not None:
        data.tariff_date = db_data['tariff_date'].strftime('%d.%m.%Y %H:%M')
    else:
        data.tariff_date = 'не оформлена'
    """ Присвоение переменных """

    return data
