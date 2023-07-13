from aiogram.utils.keyboard import ReplyKeyboardBuilder


def support():
    builder = ReplyKeyboardBuilder()

    builder.button(text='❌ Закончить разговор')

    return builder.adjust(1).as_markup(resize_keyboard=True)


def support_operator():
    builder = ReplyKeyboardBuilder()

    builder.button(text='❌ Завершить разговор')

    return builder.adjust(1).as_markup(resize_keyboard=True)
