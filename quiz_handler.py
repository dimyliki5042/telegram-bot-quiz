import db_handler as DBH
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
import json


DATA = None

def Load_Data():
    global DATA
    with open('data.json', 'r', encoding='utf-8') as file:
        DATA = json.load(file)

async def New_Quiz(message):
    await DBH.Create_User(message.from_user.id, message.from_user.username)
    await Get_Question(message, message.from_user.id)

async def Get_Question(message, user_id):
    current_question_index = await DBH.Get_Index(user_id)
    correct_index = DATA[current_question_index]['correct_option']
    options = DATA[current_question_index]['options']
    kb = Generate_Options(options, options[correct_index])
    await message.answer(f"{DATA[current_question_index]['question']}", reply_markup=kb)

def Generate_Options(options, right_answer):
    builder = InlineKeyboardBuilder()
    for option in options:
        builder.add(types.InlineKeyboardButton(text=option,
                    callback_data = f'success##{option}' if option == right_answer else f'failure##{option}'))
    builder.adjust(1)
    return builder.as_markup()