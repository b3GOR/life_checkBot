import os
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
import json

async def upload_data(user_id,state: FSMContext):
    status = await state.get_data()

    if not os.path.exists('set_profile.json'):
        with open('set_profile.json', 'w', encoding='utf-8') as f:
            data={}
            data[user_id]=status
            json.dump(data, f, ensure_ascii=False, indent=4)
    else:
        with open('set_profile.json', 'r+', encoding='utf-8') as f:
            data = json.load(f)
            if user_id not in data:
                data[user_id]=status
            data.update(status)
            f.seek(0)
            json.dump(data, f, ensure_ascii=False, indent=4)
            f.truncate()

async def edit_day(id,date,parametr,state:FSMContext):
    with open('set_profile.json','r',encoding='utf-8') as f:
        goal_parametr = json.load(f)[id][parametr]
    if not os.path.exists(f'{id}.json'):
        with open(f'{id}.json', 'w', encoding='utf-8') as f:
            template={}
            template_value = {
                        'water':{
                            'goal':0,
                            'Total_day_water':0,
                            'Day_water_history': {}
                        },
                        'calory':{
                            'goal': 0,
                            'Total_day_callory': 0,
                            'burned': 0,
                            'Day_food_history': {}
                        },
                        'activity':{
                            'Total_day_activity':0,
                            'Day_activity_history':{}

                        }}
            all_status = await state.get_data()
            param = all_status.get(parametr)
            template[date.strftime('%Y-%m-%d')] =  template_value
            template[date.strftime('%Y-%m-%d')][parametr][f'Total_day_{parametr}'] +=param
            data[date.strftime('%Y-%m-%d')][parametr]['goal'] = goal_parametr
            template[date.strftime('%Y-%m-%d')][parametr][f'Day_{parametr}_history'][date.strftime('%Y-%m-%d %H:%M')]= param
            json.dump(template,f, ensure_ascii=False, indent=4)
    else:
        with open(f'{id}.json', 'r+', encoding='utf-8') as f:
            data = json.load(f)
            all_status = await state.get_data()
            param = all_status.get(parametr)
            if  date.strftime('%Y-%m-%d') not in data:
                data[date.strftime('%Y-%m-%d')] = template_value
            data[date.strftime('%Y-%m-%d')][parametr][f'Total_day_{parametr}'] +=param
            data[date.strftime('%Y-%m-%d')][parametr]['goal'] =goal_parametr
            data[date.strftime('%Y-%m-%d')][parametr][f'Day_{parametr}_history'][date.strftime('%Y-%m-%d %H:%M:%S')]= param
            f.seek(0)
            json.dump(data, f, ensure_ascii=False, indent=4)
            f.truncate()



