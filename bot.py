import asyncio
import logging
from aiogram import F
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
import aiogram.utils.formatting as auf
import db_handler as DBH
import quiz_handler as QH


API_TOKEN = ''
BOT = Bot(token=API_TOKEN)
DP = Dispatcher()

@DP.message(Command('start'))
async def CMD_Start(message: types.message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text='Start game'))
    await message.answer('Welcome to QUIZ!', reply_markup=builder.as_markup(resize_keyboard=True))

@DP.message(F.text=='Start game')
@DP.message(Command('quiz'))
async def CMD_Quiz(message:types.message):
    await message.answer(f'Let\'s start QUIZ')
    await QH.New_Quiz(message)

@DP.callback_query(F.data.split('##')[0] == "success")
async def Right_Answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_text(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        text=f"Ваш ответ: \"{callback.data.split('##')[1]}\"",
        reply_markup=None
    )
    await callback.message.answer("Верно!")

    current_question_index = await DBH.Get_Index(callback.from_user.id)
    current_question_index += 1
    await DBH.Update_Index(callback.from_user.id, current_question_index)

    correct_answers = await DBH.Get_Answers_Count(callback.from_user.id, 'correct_answers')
    correct_answers += 1
    await DBH.Update_Answers(callback.from_user.id, correct_answers, 'correct_answers')

    if current_question_index < len(QH.DATA):
        await QH.Get_Question(callback.message, callback.from_user.id)
    else:
        await Show_Stats(callback.message, callback.from_user.id)

@DP.callback_query(F.data.split('##')[0] == "failure")
async def Wrong_answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_text(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        text=f"Ваш ответ: \"{callback.data.split('##')[1]}\"",
        reply_markup=None
    )

    current_question_index = await DBH.Get_Index(callback.from_user.id)
    correct_option = QH.DATA[current_question_index]['correct_option']
    await callback.message.answer(f"Неправильно. Правильный ответ: {QH.DATA[current_question_index]['options'][correct_option]}")

    current_question_index += 1
    await DBH.Update_Index(callback.from_user.id, current_question_index)

    wrong_answers = await DBH.Get_Answers_Count(callback.from_user.id, 'wrong_answers')
    wrong_answers += 1
    await DBH.Update_Answers(callback.from_user.id, wrong_answers, 'wrong_answers')

    if current_question_index < len(QH.DATA):
        await QH.Get_Question(callback.message, callback.from_user.id)
    else:
        await Show_Stats(callback.message, callback.from_user.id)

async def Show_Stats(message, user_id):
    all_stats, user_stats = await DBH.Get_Statistic(user_id)
    await message.answer(f'Ваша статистика: {user_stats[0]} правильных ответов и {user_stats[1]} неправильных ответов\n')
    msg = 'Общая статистика:\n'   
    for index, row in enumerate(all_stats):    
        msg += f'{index + 1}. {row[0]} ответил {row[1] * 10}% правильных ответов\n'
    await message.answer(msg)

async def main():
    logging.basicConfig(level=logging.INFO)
    QH.Load_Data()
    await DBH.Create_Table()
    await DP.start_polling(BOT)

if __name__ == '__main__':
    asyncio.run(main())