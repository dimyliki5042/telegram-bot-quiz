import aiosqlite


DB_NAME = 'quiz_bot.db'

async def Create_Table():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('CREATE TABLE IF NOT EXISTS quiz_state (user_id INTEGER PRIMARY KEY, username TEXT, question_index INTEGER default 0, ' \
        'correct_answers INTEGER default 0, wrong_answers INTEGER default 0)')
        await db.commit()

async def Create_User(user_id, username):
    async with (aiosqlite.connect(DB_NAME)) as db:
        await db.execute('INSERT OR REPLACE INTO quiz_state VALUES (?, ?, 0, 0, 0)', (user_id, username))
        await db.commit()

async def Update_Index(user_id, index):
    async with (aiosqlite.connect(DB_NAME)) as db:
        await db.execute(f'UPDATE quiz_state SET question_index = {index} WHERE user_id = {user_id}')
        await db.commit()

async def Get_Answers_Count(user_id, column):
     async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(f'SELECT {column} FROM quiz_state WHERE user_id = (?)', (user_id, )) as cursor:
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0

async def Get_Statistic(user_id):
    async with(aiosqlite.connect(DB_NAME)) as db:
        all_stats = None
        user_stats = None
        async with db.execute('SELECT username, correct_answers, wrong_answers FROM quiz_state ORDER BY correct_answers') as cursor:
            all_stats = await cursor.fetchmany(5)
        async with db.execute(f'SELECT correct_answers, wrong_answers FROM quiz_state WHERE user_id = (?)', (user_id, )) as cursor:
            user_stats = await cursor.fetchone()
        return all_stats, user_stats
    pass

async def Update_Answers(user_id, value, column):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(f'UPDATE quiz_state SET {column} = {value} WHERE user_id = {user_id}')
        await db.commit()

async def Get_Index(user_id):
     async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT question_index FROM quiz_state WHERE user_id = (?)', (user_id, )) as cursor:
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0