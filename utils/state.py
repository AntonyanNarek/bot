from aiogram.fsm.state import StatesGroup, State


class UserState(StatesGroup):
    waiting_data_company = State()


class SupportState(StatesGroup):
    waiting_user_state = State()
    waiting_operator_state = State()
