from aiogram.utils.keyboard import InlineKeyboardBuilder


def apanel_menu(status):
    builder = InlineKeyboardBuilder()

    builder.button(text=f'Бесплатный отчет: {status}', callback_data='free_order_status')
    builder.button(text='Статистика', callback_data='stats_bot')
    builder.button(text='Главное меню', callback_data='return_menu')

    return builder.adjust(1).as_markup()
