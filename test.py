import sqlite3
import asyncio
import logging
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import Update, InlineKeyboardButton, InlineKeyboardMarkup,KeyboardButton,ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import types, F, Router
from aiogram.types import Message
from aiogram.filters import Command
start_press=False
takeFIO = False
start_test = False
answer = False
question = 1 
id_test=""
FIO = ""
member = ""
count_question = 0
global users
users = []
router = Router()
builder = InlineKeyboardBuilder()
class connect_db:
    def __init__(self, db_name):
        self.db_name = db_name
        self.connector = sqlite3.connect(self.db_name)
        self.cursor = self.connector.cursor()
    def select_sql(self,sql_txt):
        self.sql_txt = sql_txt
        return  self.cursor.execute(self.sql_txt)
    def close_db(self):
        self.connector.commit()
        self.cursor.close()
        self.connector.close()


async def main():
    global bot
    bot = Bot(token='7728863257:AAFiNfCtlIDN-DN9IN6WyIMbTAo8lVF7lqI', parsemode=ParseMode.HTML)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
@router.message(Command("start"))
async def start_handler(msg: Message):
    NoUsers = True
    global users
    for i in range(len(users)):
        if users[i-1][0] == msg.from_user.id:
            
            NoUsers =False
            break
        else:
            NoUsers =True
    await bot.send_message(chat_id=msg.from_user.id,text="Привет! Я бот проводящий тесты, напиши свой код для теста.")
    if NoUsers:
        users.append([msg.from_user.id,True,False,False,False,1,"","","",0])#[айди пользователя,использован ли start,Запрашивать ФИО,Начат ли тест,Отвечает пользователь?,№ вопроса в тесте,айди теста,Фио,Код,Кол-во вопросов в тесте]
    print(users)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for i in range(len(users)):
        if users[i-1][0] == context._user_id:
            answer= users[i-1][4]
            question= users[i-1][5]
            id_test= users[i-1][6]
            FIO= users[i-1][7]
            member= users[i-1][8]
    query = update.callback_query
    await query.answer()

    # Извлекаем номер кнопки из callback_data
    msgnew = query.data.split("_")[1]
    db = connect_db('autoservis_users.db')
    sql = db.select_sql("SELECT * from Questions"+str(id_test))
    for row in sql:
        db_id = row[0]
        db_question = row[1]
        db_count_answer = row[2]
        db_id_answer_true = row[3]
        db_answer = row[4]
        if question == db_id:
            if db_count_answer !="1":
                if str(db_id_answer_true).lower() == msgnew.lower():
                    sql = db.select_sql(
            f"INSERT INTO 'Questions{id_test}_result' (question,answer_true,answer,result,FIO,code_member) VALUES('{db_question}','{db_id_answer_true}','{str(msgnew)}','Верно','{FIO}','{member}');")
                    
                else:
                    sql = db.select_sql(
            f"INSERT INTO 'Questions{id_test}_result' (question,answer_true,answer,result,FIO,code_member) VALUES('{db_question}','{db_id_answer_true}','{str(msgnew)}','Неверно','{FIO}','{member}');")
            else:
                if str(db_answer).lower() == msgnew.lower():
                    sql = db.select_sql(
            f"INSERT INTO 'Questions{id_test}_result' (question,answer_true,answer,result,FIO,code_member) VALUES('{db_question}','{db_answer}','{str(msgnew)}','Верно','{FIO}','{member}');")
                    
                else:
                    sql = db.select_sql(
            f"INSERT INTO 'Questions{id_test}_result'(question,answer_true,answer,result,FIO,code_member) VALUES('{db_question}','{db_answer}','{str(msgnew)}','Неверно','{FIO}','{member}');")
            answer = False
            question +=1
    for i in range(len(users)):
        if users[i-1][0] == context._user_id:
            users[i-1][4] = answer
            users[i-1][5] = question
            users[i-1][6] = id_test
            users[i-1][7] = FIO
            users[i-1][8] = member
            keyboard = [[KeyboardButton("/continue")]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

            await update.message.reply_text(reply_markup=reply_markup)
            break
    print(users)
    db.close_db()
@router.message(Command("continue"))
@router.message()
async def message_handler(msg: Message):
    global users
    for i in range(len(users)):
        if users[i-1][0] == msg.from_user.id:
            start_press = users[i-1][1]
            takeFIO= users[i-1][2]
            start_test= users[i-1][3]
            answer= users[i-1][4]
            question= users[i-1][5]
            id_test= users[i-1][6]
            FIO= users[i-1][7]
            member= users[i-1][8]
            count_question= users[i-1][9]
            if takeFIO:
                FIO = str(msg.md_text)
                start_test = True
                takeFIO = False
            if start_press:
                if not(start_test):
                    code = str(msg.md_text)
                    db = connect_db('autoservis_users.db')
                    sql = db.select_sql("SELECT * from Codes_members")
                    for row in sql:
                        db_id = row[0]
                        db_code = row[1]
                        db_id_test = row[2]
                        if code == db_code:
                            id_test=db_id_test
                            open = True
                            break
                        else:
                            open = False
                    db.close_db()
                    if open:
                        member = db_code
                        db = connect_db('autoservis_users.db')
                        sql = db.select_sql(f"SELECT id from Questions{id_test}_result where code_member={member}")
                        for row in sql:
                            id = row[0]
                            if str(id) == "":
                                open = True
                                break
                            else:
                                open = False
                        db.close_db()
                        if open:
                            db = connect_db('autoservis_users.db')
                            sql = db.select_sql("SELECT * from table_tests")
                            for row in sql:
                                db_id = row[0]
                                db_count_question = row[4]
                                if id_test == db_id:
                                    count_question = db_count_question
                                    open = True
                                    break
                                else:
                                    open = False
                            if open:
                                await msg.answer(f"Успешный вход к тесту")
                                await msg.answer(f"Загрузка теста...Успешна! Введите ФИО")
                                
                                takeFIO = True
                                db.close_db()
                            else:
                                await msg.answer(f"Успешный вход к тесту")
                                await msg.answer(f"Загрузка теста...Ошибка. Тест не найден")
                                db.close_db()
                        else:
                            await msg.answer(f"Человек с таким кодом уже проходил тест")
                    else:
                        await msg.answer(f"Нет такого кода(")
                        await msg.answer(f"Возращайся когда будет код для теста")
                else:
                    if answer:
                        msgnew = msg.md_text.replace("\.",".")
                        msgnew = msgnew.replace("\-","-")
                        msgnew = msgnew.replace("\+","+")
                        msgnew = msgnew.replace("\*","*")
                        db = connect_db('autoservis_users.db')
                        sql = db.select_sql("SELECT * from Questions"+str(id_test))
                        for row in sql:
                            db_id = row[0]
                            db_question = row[1]
                            db_count_answer = row[2]
                            db_id_answer_true = row[3]
                            db_answer = row[4]
                            if question == db_id:
                                if db_count_answer !="1":
                                    if str(db_id_answer_true).lower() == msgnew.lower():
                                        sql = db.select_sql(
                                f"INSERT INTO 'Questions{id_test}_result' (question,answer_true,answer,result,FIO,code_member) VALUES('{db_question}','{db_id_answer_true}','{str(msgnew)}','Верно','{FIO}','{member}');")
                                        
                                    else:
                                        sql = db.select_sql(
                                f"INSERT INTO 'Questions{id_test}_result' (question,answer_true,answer,result,FIO,code_member) VALUES('{db_question}','{db_id_answer_true}','{str(msgnew)}','Неверно','{FIO}','{member}');")
                                else:
                                    if str(db_answer).lower() == msgnew.lower():
                                        sql = db.select_sql(
                                f"INSERT INTO 'Questions{id_test}_result' (question,answer_true,answer,result,FIO,code_member) VALUES('{db_question}','{db_answer}','{str(msgnew)}','Верно','{FIO}','{member}');")
                                        
                                    else:
                                        sql = db.select_sql(
                                f"INSERT INTO 'Questions{id_test}_result'(question,answer_true,answer,result,FIO,code_member) VALUES('{db_question}','{db_answer}','{str(msgnew)}','Неверно','{FIO}','{member}');")
                                answer = False
                                question +=1
                                
                        db.close_db()
                    db = connect_db('autoservis_users.db')
                    sql = db.select_sql("SELECT * from Questions"+str(id_test))
                    for row in sql:
                        db_id = row[0]
                        db_question = row[1]
                        db_count_answer = row[2]
                        db_id_answer_true = row[3]
                        db_answer = row[4] 
                        if question>count_question:
                            await msg.answer(f"Больше вопросов нет!")
                            
                            start_press = False
                            start_test = False
                            break
                        if question == db_id:
                            await msg.answer(f"Вопрос{str(question)}: {db_question}")
                            
                            if db_count_answer !="1":
                                
                                for i in range(1, int(db_count_answer) + 1):
                                    builder.button(text=f"Кнопка {i}", callback_data=f"btn_{i}")
                                # ✅ Создаём reply_markup ОДИН раз, после цикла
                                reply_markup = builder.as_markup()

                                # Отправляем сообщение
                                await msg.answer("Нажмите на правильный ответ.", reply_markup=reply_markup)
                            answer = True
                            break
                        
                    db.close_db()
                        
                    
            for i in range(len(users)):
                if users[i-1][0] == msg.from_user.id:
                    users[i-1][1] = start_press
                    users[i-1][2] = takeFIO
                    users[i-1][3] = start_test
                    users[i-1][4] = answer
                    users[i-1][5] = question
                    users[i-1][6] = id_test
                    users[i-1][7] = FIO
                    users[i-1][8] = member
                    users[i-1][9] = count_question
                    break
            print(users)
            break
        else:
            pass


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())