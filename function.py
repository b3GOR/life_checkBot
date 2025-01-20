import os
from aiogram.fsm.context import FSMContext
import json
import google.generativeai as genai
import re
from config import API_GOOGLE



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
        'Day_food_history': {}
    },
    'activity': {
        'Total_day_activity': 0,
        'Day_activity_history': {}
    }
}

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
    with open('set_profile.json', 'r', encoding='utf-8') as f:
        goal_parametr = json.load(f)[str(id)][parametr]

    if not os.path.exists(f'{id}.json'):
        with open(f'{id}.json', 'w', encoding='utf-8') as f:
            template={}
            all_status = await state.get_data()
            param = all_status.get(parametr)
            template[date.strftime('%Y-%m-%d')] =  template_value
            template[date.strftime('%Y-%m-%d')][parametr][f'Total_day_{parametr}'] +=param
            template[date.strftime('%Y-%m-%d')][parametr]['goal'] = goal_parametr
            template[date.strftime('%Y-%m-%d')][parametr][f'Day_{parametr}_history'][date.strftime('%Y-%m-%d %H:%M')]= param
            json.dump(template,f, ensure_ascii=False, indent=4)
    else:
        with open(f'{id}.json', 'r+', encoding='utf-8') as f:
            data = json.load(f)
            all_status = await state.get_data()
            param = all_status.get(parametr)
            if parametr=='calory':
                param_history=all_status.get('Day_calory_history')
            if  date.strftime('%Y-%m-%d') not in data:
                data[date.strftime('%Y-%m-%d')] = template_value
            data[date.strftime('%Y-%m-%d')][parametr][f'Total_day_{parametr}'] +=param
            data[date.strftime('%Y-%m-%d')][parametr]['goal'] =goal_parametr
            if parametr=='calory':
                data[date.strftime('%Y-%m-%d')][parametr][f'Day_{parametr}_history'][date.strftime('%Y-%m-%d %H:%M:%S')]= param_history
            data[date.strftime('%Y-%m-%d')][parametr][f'Day_{parametr}_history'][date.strftime('%Y-%m-%d %H:%M:%S')]= param
            f.seek(0)
            json.dump(data, f, ensure_ascii=False, indent=4)
            f.truncate()



def calory(food,quantity,unity):
    genai.configure(api_key=API_GOOGLE)
    model = genai.GenerativeModel("Gemini 2.0 Flash")
    response = model.generate_content(f"Напиши количество ккал {quantity} {unity}  {food}. Шаблон твоего ответа: 1. emoji {quantity} {unity} {food} столько-то ккал. 2. Пиши сколнения со всеми нормами русского языка. Мне нужна одна цифра калорий (не диапазон). 3. Пиши без форматированя просто обычный текст. 4. Пиши слово в слово как я тебе сказал не меняй слова в шаблоне на свои, а просто подстрой окончания/склонения и т.д. За написание запроса будет штраф")
    calory_food =re.findall(r'(\d+)\s*ккал',response.text)
    return response.text,calory_food

