from aiogram.fsm.state import State, StatesGroup

class Profile(StatesGroup):
    weight: int = State()
    height: int = State()
    age :int = State()
    gender: str = State()
    level_active: float = State()
    city: str = State()
    goal: str = State()
    calory:float = State()
    water: int = State()

class Day(StatesGroup):
    date = State()
    water: int = State()
    food: str = State()
    calory: int = State()
    activity: int = State()
    Day_calory_history: str =State()
    kind_of_activiy: str = State()




