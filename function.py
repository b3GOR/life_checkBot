import os
from aiogram.fsm.context import FSMContext
import aiohttp
import json
from config import API_NINJA
from bs4 import BeautifulSoup





template_value = {
    'water': {
        'goal': 0,
        'Total_day_water': 0,
        'Day_water_history': {}
    },
    'calory': {
        'goal': 0,
        'Total_day_calory': 0,
        'burned': 0,
        'Day_calory_history': {}
    },
    'activity': {
        'goal':0,
        'Total_day_activity': 0,
        'Day_activity_history': {}
    }
}

async def upload_data(user_id,state: FSMContext):
    status = await state.get_data()
    if not os.path.exists('profiles'):
        os.makedirs('profiles')
    if not os.path.exists('profiles/set_profile.json'):
        with open('profiles/set_profile.json', 'w', encoding='utf-8') as f:
            data={}
            data[user_id]=status
            data[user_id]['activity'] = 300
            json.dump(data, f, ensure_ascii=False, indent=4)
    else:
        with open('profiles/set_profile.json', 'r+', encoding='utf-8') as f:
            data = json.load(f)
            if user_id not in data:
                data[user_id]=status
            data.update(status)
            data[user_id]['activity'] = 300
            f.seek(0)
            json.dump(data, f, ensure_ascii=False, indent=4)
            f.truncate()

async def edit_day(id,date,parametr,state:FSMContext):
    with open('profiles/set_profile.json', 'r', encoding='utf-8') as f:
        goal_parametr = json.load(f)[str(id)][parametr]

    if not os.path.exists(f'profiles/{id}.json'):
        with open(f'profiles/{id}.json', 'w', encoding='utf-8') as f:
            template={}
            all_status = await state.get_data()
            if parametr=='activity':
                param1=all_status.get('time_activity')
                param2=all_status.get('burned')

                template[date.strftime('%Y-%m-%d')] =  template_value
                template[date.strftime('%Y-%m-%d')][parametr][f'Total_day_{parametr}'] += param1
                template[date.strftime('%Y-%m-%d')][parametr]['goal'] = goal_parametr
                template[date.strftime('%Y-%m-%d')][parametr][f'Day_{parametr}_history'][date.strftime('%Y-%m-%d %H:%M:%S')]= param1
                template[date.strftime('%Y-%m-%d')]['calory']['burned'] += param2
            elif parametr=='water':
                param = all_status.get(parametr)
                template[date.strftime('%Y-%m-%d')] =  template_value
                template[date.strftime('%Y-%m-%d')][parametr][f'Total_day_{parametr}'] +=param
                template[date.strftime('%Y-%m-%d')][parametr]['goal'] = goal_parametr
                template[date.strftime('%Y-%m-%d')][parametr][f'Day_{parametr}_history'][date.strftime('%Y-%m-%d %H:%M:%S')]= param
            elif parametr=='calory':
                param = all_status.get(parametr)
                template[date.strftime('%Y-%m-%d')] =  template_value
                template[date.strftime('%Y-%m-%d')][parametr][f'Total_day_{parametr}'] +=param
                template[date.strftime('%Y-%m-%d')][parametr]['goal'] = goal_parametr
                template[date.strftime('%Y-%m-%d')][parametr][f'Day_{parametr}_history'][date.strftime('%Y-%m-%d %H:%M:%S')]= param
            json.dump(template,f, ensure_ascii=False, indent=4)
    else:
        with open(f'profiles/{id}.json', 'r+', encoding='utf-8') as f:
            data = json.load(f)
            all_status = await state.get_data()
            if parametr=='activity':
                param1=all_status.get('time_activity')
                param2=all_status.get('burned')
                data[date.strftime('%Y-%m-%d')] =  template_value
                data[date.strftime('%Y-%m-%d')][parametr][f'Total_day_{parametr}'] +=param1
                data[date.strftime('%Y-%m-%d')][parametr]['goal'] = goal_parametr
                data[date.strftime('%Y-%m-%d')][parametr][f'Day_{parametr}_history'][date.strftime('%Y-%m-%d %H:%M:%S')]= param1
                data[date.strftime('%Y-%m-%d')]['calory']['burned'] += param2
            elif parametr=='water':
                param = all_status.get(parametr)
                data[date.strftime('%Y-%m-%d')] =  template_value
                data[date.strftime('%Y-%m-%d')][parametr][f'Total_day_{parametr}'] +=param
                data[date.strftime('%Y-%m-%d')][parametr]['goal'] = goal_parametr
                data[date.strftime('%Y-%m-%d')][parametr][f'Day_{parametr}_history'][date.strftime('%Y-%m-%d %H:%M:%S')]= param
            elif parametr=='calory':
                param = all_status.get(parametr)
                data[date.strftime('%Y-%m-%d')] =  template_value
                data[date.strftime('%Y-%m-%d')][parametr][f'Total_day_{parametr}'] +=param
                data[date.strftime('%Y-%m-%d')][parametr]['goal'] = goal_parametr
                data[date.strftime('%Y-%m-%d')][parametr][f'Day_{parametr}_history'][date.strftime('%Y-%m-%d %H:%M:%S')]= param
            f.seek(0)
            json.dump(data, f, ensure_ascii=False, indent=4)
            f.truncate()


async def calc_calory(product,gramm):
    search_root = product.lower()[:5]
    async with aiohttp.ClientSession() as session:
        async with session.get('https://lenta.ru/articles/2024/04/10/tablitsa-kaloriinosti/') as request:
            response= await request.text()
    soup = BeautifulSoup(response, 'html.parser')
    rows = soup.find_all('tr')
    
    found_products = []
    
    for i, row in enumerate(rows, 1):
        first_cell = row.find(['th', 'td'])
        if not first_cell:
            continue
            
        cell_text = first_cell.get_text(strip=True).lower()
        if search_root in cell_text:
            calories = int(row.find_all('td')[-1].get_text(strip=True)) if row.find_all('td') else None
            finaly_calories = int((gramm*calories)/100)
            found_products.append(f"В {gramm} г продукта '{first_cell.get_text(strip=True)}' содержится {finaly_calories} ккал")
    
    if found_products:
        return finaly_calories,"\n".join(found_products)
    return f"Продукты содержащие '{search_root}' не найдены"







async def check_progress(id,date):
    with open(f'profiles/{id}.json','r',encoding='utf-8') as f:
        data = json.load(f)
    result = f'''

\U0001F4CA <b>Статистика за {date}</b>

<i>Вода</i>:
- Выпито: {data[date]['water']['Total_day_water']} мл из {data[date]['water']['goal']} мл.
- Осталось: {(data[date]['water']['goal'])-(data[date]['water']['Total_day_water'])} мл.

<i>Калории</i>:
- Потреблено: {data[date]['calory']['Total_day_calory']} ккал из {data[date]['calory']['goal']} ккал.
- Сожжено: {data[date]['calory']['burned']} ккал.
- Осталось: {(data[date]['calory']['goal'])-(data[date]['calory']['Total_day_calory'])} ккал.
'''
    return result

async def burned_calory(state:FSMContext):
    speed_dict={
        '5':'Running, 5 mph (12 minute mile)',
        '5.2':'Running, 5.2 mph (11.5 minute mile)',
        '6':'Running, 6 mph (10 min mile)',
        '6.7':'Running, 6.7 mph (9 min mile)',
        '7':'Running, 7 mph (8.5 min mile)',
        '7.5':'Running, 7.5mph (8 min mile)',
        '8':'Running, 8 mph (7.5 min mile)',
        '8.6':'Running, 8.6 mph (7 min mile)',
        '9':'Running, 9 mph (6.5 min mile)',
        '10':'Running, 10 mph (6 min mile)',

    }
    data = await state.get_data()
    kind_of_activity = data.get('activity')
    time_activity = data.get('time_activity')
    speed = data.get('speed_activity')
    if kind_of_activity=='walk':
        active_req='Walking the dog'
    elif kind_of_activity=='run':
        active_req=speed_dict[str(speed)]
    elif kind_of_activity=='workout':
        active_req='Weight lifting, light workout'




    async with  aiohttp.ClientSession() as session:
        async with session.get(f'https://api.api-ninjas.com/v1/caloriesburned?activity={active_req}&duration={time_activity}',headers={'X-Api-Key': API_NINJA}) as request:
            response_data =  await request.json()
            response=response_data[0]['total_calories']
    
    return response,time_activity,kind_of_activity
            