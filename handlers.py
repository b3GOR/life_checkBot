from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message,InlineKeyboardMarkup,InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
import asyncio
import aiohttp
from config import API_NUTRITION
from states import Profile, Day
from aiogram.enums import ParseMode
from function import upload_data, edit_day
router = Router()

@router.message(Command('start'))
async def cmd_start(message:Message):
    await message.reply('Добро пожаловать! Я ваш бот. \n'
                        'Ведите /help для списка команд')
    

@router.message(Command('help'))
async def help(message: Message):
    await message.answer(
        'Доступные команды \n'
        '/set_profile - Запись личной информации \n'
        '/log_water <количество (мл)> - Запись воды \n'
        '/log_food <название продукта> - Запись еды \n'
        '/log_workout <тип тренировки> <время (мин)> - Запись активности \n'
        '/check_progress - Прогресс \n'
    )



@router.message(Command('set_profile'))
async def set_profile(message: Message,state:FSMContext):
    await message.answer('Давайте укажем ваши параметры')
    await asyncio.sleep(0.5) 
    await message.answer('Укажите ваш вес (кг)')
    await state.set_state(Profile.weight)



@router.message(Profile.weight)
async def height(message: Message, state: FSMContext):
    await state.update_data(weight=int(message.text))
    await message.answer('Введите ваш рост (см)')
    await state.set_state(Profile.height)

@router.message(Profile.height)
async def age(message: Message,state:FSMContext):
    await state.update_data(height=int(message.text))
    await message.answer('Введите ваш возраст')
    await state.set_state(Profile.age)

@router.message(Profile.age)
async def level_activity(message: Message,state:FSMContext):
    await state.update_data(age=int(message.text))
    await message.answer('Дневная активность')
    button = InlineKeyboardMarkup(
        inline_keyboard=[
        [InlineKeyboardButton(text='1', callback_data='1')],
        [InlineKeyboardButton(text='2', callback_data='2')],
        [InlineKeyboardButton(text='3', callback_data='3')],
        [InlineKeyboardButton(text='4', callback_data='4')],
        [InlineKeyboardButton(text='5', callback_data='5')]
        ]
    )
    await message.answer(
                         '1. <b>Очень низкая</b> -  — Редко выхожу из дома, почти весь день сижу \n' 
                         '2. <b>Низкая</b> - Хожу в магазин или недолго прогуливаюсь \n' 
                         '3. <b>Средняя</b> - Ежедневно гуляю не меньше часа \n' 
                         '4. <b>Высокая</b> - Занимаюсь активными видами спорта/досуга (велосипед, ролики, лыжи, коньки и др.) 2-3 раза в неделю\n' 
                         '5. <b>Очень высокая</b> - Регулярно занимаюсь спортом (бег, гимнастика, тренажерный зал), минимум 5 раз в недел \n'
                         ,parse_mode=ParseMode.HTML, reply_markup=button
    ) 
    await state.set_state(Profile.level_active)
@router.callback_query(Profile.level_active)
async def upload_level_acitivty(callback: CallbackQuery,state: FSMContext):
    level_active = None
    if callback.data == '1':
        level_active = 1.4
    elif callback.data == '2':
        level_active = 1.6
    elif callback.data == '3':
        level_active = 1.9
    elif callback.data == '4':
        level_active = 2.2
    else:
        level_active = 2.5
    await state.update_data(level_active=level_active)

    await state.set_state(Profile.gender)
    buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Мужской',callback_data='male')],
            [InlineKeyboardButton(text='Женский',callback_data='female')]
        ]
    )
    await callback.message.answer('Укажите пол?', reply_markup= buttons)

@router.callback_query(Profile.gender)
async def gender_callback(callback: CallbackQuery, state: FSMContext):
    await state.update_data(gender=callback.data)
    await callback.message.answer('Укажите ваш город')
    await state.set_state(Profile.city)



@router.message(Profile.city)
async def level_activity(message: Message,state:FSMContext):
    await state.update_data(city=message.text)
    await state.set_state(Profile.goal)
    buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Снижение веса',callback_data='low')],
            [InlineKeyboardButton(text='Поддержание веса',callback_data='support')],
            [InlineKeyboardButton(text='Набор веса',callback_data='up')]
        ]
    )
    await message.answer('Какова ваша цель?', reply_markup= buttons)

@router.callback_query(Profile.goal)
async def goal(callback_query: CallbackQuery, state: FSMContext):
    purpose = callback_query.data
    await state.update_data(goal=purpose)
    await callback_query.message.answer('Расчет нормы каллорий в день')
    await asyncio.sleep(1)
    await state.set_state(Profile.callory)
    data = await state.get_data()
    level_active= data.get('level_active')
    height = data.get('height')
    age = data.get('age')
    weight = data.get('weight')
    gender = data.get('gender')
    goal = data.get('goal')
    
    if gender == 'female':
        callorium = ((10 * weight) + (6.25 * height) - (5 * age) - 161)
        callorium *= float(level_active)
    else: 
        callorium = ((10 * weight) + (6.25 * height) - (5 * age) + 5)
        callorium *= float(level_active)

    if goal=='low':
        callorium -=callorium*0.2
    elif goal =='up':
        callorium+=callorium*0.2
    
    # button = InlineKeyboardMarkup( inline_keyboard=[
    #     [InlineKeyboardButton(text='Оставить', callback_data='stay')],
    #     [InlineKeyboardButton(text='Редактировать', callback_data='edit')]
    # ])
    await state.update_data(callory = round(callorium))
    water = round(30 * weight)
    await state.update_data(water=water)
    await upload_data(user_id=callback_query.from_user.id,state=state)

    await callback_query.message.answer(f'Ваша норма каллорий в день {callorium} ккал. \n'
                                        f'Норма потребления воды в день {water} \n'
                                        'Данные дневного потребления каллорий успешно сохранены') 
    
    await state.clear()

    


@router.message(Command('log_water'))
async def log_water(message: Message,state: FSMContext):
    await message.answer('Укажите количество выпитой воды (мл)')
    await state.set_state(Day.water)
@router.message(Day.water)
async def write_water(message: Message,state:FSMContext):
    await state.update_data(water=int(message.text))
    await edit_day(message.from_user.id,message.date,'water',state)
    await message.answer('Данные о воде обновлены')
    await state.clear()

        

@router.message(Command('log_food'))
async def log_food(message: Message,state: FSMContext):
    await message.answer('Введите продукт/блюдо и количество его грамм')
    await state.set_state(Day.callory)
@router.message(Day.callory)
async def write_calory(message: Message,state: FSMContext):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://api.api-ninjas.com/v1/nutrition?query={message.text}',headers={'X-Api-Key': f'{API_NUTRITION}'}) as request:
            response = request.json()['calories']
    await state.update_data(callory=float(response))
    await edit_day(message.from_user.id,message.date,'calory',state)
    await message.answer('Данные о еде обновлены')
    await state.clear()


@router.message(Command('log_activity'))
async def log_activity(message: Message):
    pass

@router.message(Command('check_progress'))
async def check_progress(message: Message):
    pass


    




