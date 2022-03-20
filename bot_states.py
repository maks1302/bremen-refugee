from aiogram.dispatcher.filters.state import State, StatesGroup


class Add(StatesGroup):
    # State for adding/editing messages

    role = State()
    district = State()
    date = State()
    time = State()
