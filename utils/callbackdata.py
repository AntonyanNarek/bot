from aiogram.filters.callback_data import CallbackData


class TariffData(CallbackData, prefix='tariff_data'):
    title: str
    count: int
    price: int


class SupportData(CallbackData, prefix='support_data'):
    user_id: int
