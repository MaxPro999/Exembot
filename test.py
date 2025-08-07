import sqlite3
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command  # ✅ Этот импорт был добавлен!
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.default import DefaultBotProperties
# === Глобальные переменные (оставлены как в оригинале) ===
start_press = False
takeFIO = False
start_test = False
answer = False
question = 1
id_test = ""
FIO = ""
member = ""
count_question = 0

# Список пользователей: [id, start_press, takeFIO, start_test, answer, question, id_test, FIO, member, count_question]
users = []

# Создаём роутер для обработки сообщений
router = Router()

# ВАЖНО: НЕ создавайте builder глобально — он будет накапливать кнопки!
# builder = InlineKeyboardBuilder()  # ❌ Убрали глобально!

# === Подключение к базе данных ===
class connect_db:
    def __init__(self, db_name):
        self.db_name = db_name
        self.connector = sqlite3.connect(self.db_name)
        self.cursor = self.connector.cursor()

    def select_sql(self, sql_txt):
        """Выполняет SQL-запрос и возвращает результат"""
        self.sql_txt = sql_txt
        return self.cursor.execute(sql_txt)

    def close_db(self):
        """Сохраняет изменения и закрывает соединение"""
        self.connector.commit()
        self.cursor.close()
        self.connector.close()


# === Обработчик команды /start ===
@router.message(Command("start"))
async def start_handler(msg: Message):
    global users
    user_id = msg.from_user.id
    NoUsers = True

    # Проверяем, есть ли пользователь в списке
    for user in users:
        if user[0] == user_id:
            NoUsers = False
            break

    # Отправляем приветствие
    await bot.send_message(
        chat_id=user_id,
        text="Привет! Я бот, проводящий тесты. Напиши свой код для теста."
    )

    # Если пользователя нет — добавляем
    if NoUsers:
        users.append([user_id, True, False, False, False, 1, "", "", "", 0])

    print("Текущий список пользователей:", users)


# === НОВЫЙ: Обработчик нажатий на inline-кнопки (вместо устаревшего button_handler) ===
@router.callback_query(F.data.startswith("btn_"))
async def callback_query_handler(callback_query: types.CallbackQuery):
    global users
    user_id = callback_query.from_user.id

    # Находим данные пользователя
    user_data = None
    user_index = -1
    for i, user in enumerate(users):
        if user[0] == user_id:
            user_data = user
            user_index = i
            break

    # Если пользователь не найден или не ожидается ответ — выходим
    if not user_data or not user_data[4]:  # user_data[4] — это "answer"
        await callback_query.answer("Нажатие неактуально.")
        return

    # Извлекаем данные пользователя
    _, start_press, takeFIO, start_test, answer, question, id_test, FIO, member, count_question = user_data

    # Получаем номер нажатой кнопки (например, из "btn_2" → 2)
    button_num = callback_query.data.split("_")[1]

    # Подключаемся к БД, чтобы проверить правильность ответа
    db = connect_db('autoservis_users.db')
    sql = db.select_sql(f"SELECT * FROM Questions{id_test}")
    correct = False
    current_question_text = ""

    for row in sql:
        db_id = row[0]
        db_question = row[1]
        db_count_answer = row[2]
        db_id_answer_true = row[3]
        # db_answer = row[4]  # не используется для выбора из кнопок

        if question == db_id:
            current_question_text = db_question
            # Проверяем, совпадает ли номер кнопки с правильным ответом
            if str(db_id_answer_true) == button_num:
                correct = True
            break

    db.close_db()

    # Записываем результат в БД
    result_text = "Верно" if correct else "Неверно"
    db = connect_db('autoservis_users.db')
    db.select_sql(
        f"INSERT INTO 'Questions{id_test}_result' "
        f"(question, answer_true, answer, result, FIO, code_member) "
        f"VALUES('{current_question_text}', '{db_id_answer_true}', '{button_num}', '{result_text}', '{FIO}', '{member}');"
    )
    db.close_db()

    # Обновляем состояние: ответ засчитан, переходим к следующему вопросу
    answer = False
    question += 1

    # Сохраняем обновлённые данные
    users[user_index][4] = answer  # больше не ждём ответ
    users[user_index][5] = question  # следующий вопрос

    # Подтверждаем нажатие
    await callback_query.answer("✅ Ответ засчитан")

    # Редактируем сообщение, чтобы показать, что ответ принят
    await callback_query.message.edit_text(f"Ответ #{button_num} засчитан.")

    # Ждём 1 секунду перед следующим вопросом
    await asyncio.sleep(1)

    # Пытаемся показать следующий вопрос
    db = connect_db('autoservis_users.db')
    sql = db.select_sql(f"SELECT * FROM Questions{id_test}")
    found_next = False

    for row in sql:
        db_id = row[0]
        db_question = row[1]
        db_count_answer = row[2]
        db_id_answer_true = row[3]
        db_answer = row[4]
        # Если нашли следующий вопрос и он в пределах количества
        if question == db_id and question <= count_question:
            if db_count_answer != "1":
                db_answer=db_answer.split('; \n')
                # Создаём новую клавиатуру (важно: не глобальную!)
                builder = InlineKeyboardBuilder()
                for i in range(1, int(db_count_answer) + 1):
                    builder.button(text=f"Вариант {str(db_answer[i-1])}", callback_data=f"btn_{i}")
                builder.adjust(1)  # Каждая кнопка — на новой строке

                # Отправляем вопрос с кнопками
                await callback_query.message.answer(
                    f"Вопрос {question}: {db_question}",
                    reply_markup=builder.as_markup()
                )
            else:
                await callback_query.message.answer(
                    f"Вопрос {question}: {db_question}")
            # Обновляем, что пользователь ожидает ответ
            users[user_index][4] = True
            found_next = True
            break

    db.close_db()

    # Если вопросов больше нет
    if not found_next:
        await callback_query.message.answer("✅ Тест завершён! Спасибо за участие.")
        users[user_index][3] = False  # start_test = False
        users[user_index][4] = False  # answer = False


# === Основной обработчик сообщений: /continue и обычные сообщения ===
@router.message(Command("continue"))
@router.message()
async def message_handler(msg: Message):
    global users
    user_id = msg.from_user.id

    # Находим пользователя в списке
    user_data = None
    user_index = -1
    for i, user in enumerate(users):
        if user[0] == user_id:
            user_data = user
            user_index = i
            break

    # Если пользователь не найден — выходим
    if not user_data:
        return

    # Распаковываем данные пользователя
    user_id, start_press, takeFIO, start_test, answer, question, id_test, FIO, member, count_question = user_data

    # === Этап 1: Ввод ФИО ===
    if takeFIO:
        FIO = msg.text  # Сохраняем ФИО
        start_test = True
        takeFIO = False
        await msg.answer("✅ ФИО сохранено. Начинаем тест...")

    # === Этап 2: Ввод кода для входа в тест ===
    if start_press and not start_test:
        code = msg.text
        db = connect_db('autoservis_users.db')
        sql = db.select_sql("SELECT * FROM Codes_members")
        open = False

        for row in sql:
            db_code = row[1]
            db_id_test = row[2]
            if code == db_code:
                id_test = db_id_test
                member = db_code
                open = True
                break

        db.close_db()

        if not open:
            await msg.answer("❌ Нет такого кода. Попробуйте снова.")
            return

        # Проверяем, не проходил ли уже этот пользователь тест
        db = connect_db('autoservis_users.db')
        sql = db.select_sql(f"SELECT id FROM Questions{id_test}_result WHERE code_member = '{member}'")
        already_passed = False
        for _ in sql:
            already_passed = True
            break
        db.close_db()

        if already_passed:
            await msg.answer("⚠️ Вы уже проходили этот тест.")
            return

        # Получаем количество вопросов
        db = connect_db('autoservis_users.db')
        sql = db.select_sql("SELECT * FROM table_tests")
        open = False
        for row in sql:
            db_id = row[0]
            db_count_question = row[4]
            if str(id_test) == str(db_id):
                count_question = db_count_question
                open = True
                break
        db.close_db()

        if not open:
            await msg.answer("❌ Ошибка: тест не найден.")
            return

        await msg.answer("✅ Успешный вход в тест!")
        await msg.answer("📝 Введите ваше ФИО:")
        takeFIO = True

    # === Этап 3: Прохождение теста (обработка ответов) ===
    elif start_test and answer:
        # Обработка текстового ответа (если тип вопроса — открытый)
        msgnew = msg.text.replace("\.", ".").replace("\-", "-").replace("\+", "+").replace("\*", "*")

        db = connect_db('autoservis_users.db')
        sql = db.select_sql(f"SELECT * FROM Questions{id_test}")
        for row in sql:
            db_id = row[0]
            db_question = row[1]
            db_count_answer = row[2]
            db_id_answer_true = row[3]
            db_answer = row[4]

            if question == db_id:
                # Проверка ответа
                is_correct = False
                if db_count_answer != "1":
                    db_answer=db_answer.split('; \n')
                    builder = InlineKeyboardBuilder() 
                    for i in range(1, int(db_count_answer) + 1):
                        builder.button(text=f"Вариант {str(db_answer[i-1])}", callback_data=f"btn_{i}")
                    builder.adjust(1)
                    await msg.answer("Выберите ответ:", reply_markup=builder.as_markup())
                else:
                    # Это открытый вопрос — сравниваем текст
                    if str(db_answer).lower() == msgnew.lower():
                        is_correct = True

                # Сохраняем результат
                db.close_db()
                result_text = "Верно" if is_correct else "Неверно"
                db = connect_db('autoservis_users.db')
                db.select_sql(
                    f"INSERT INTO 'Questions{id_test}_result' "
                    f"(question, answer_true, answer, result, FIO, code_member) "
                    f"VALUES('{db_question}', '{db_id_answer_true if db_count_answer != '1' else db_answer}', "
                    f"'{msgnew}', '{result_text}', '{FIO}', '{member}');"
                )
                answer = False
                question += 1
                break
        db.close_db()

    # === Этап 4: Показ следующего вопроса ===
    if start_test and not answer and question <= count_question:
        db = connect_db('autoservis_users.db')
        sql = db.select_sql(f"SELECT * FROM Questions{id_test}")
        found = False

        for row in sql:
            db_id = row[0]
            db_question = row[1]
            db_count_answer = row[2]
            db_id_answer_true = row[3]
            db_answer = row[4]
            if question == db_id:
                await msg.answer(f"Вопрос {question}: {db_question}")

                # Если вопрос с выбором — показываем кнопки
                if db_count_answer != "1":
                    db_answer=db_answer.split('; \n')
                    builder = InlineKeyboardBuilder()  # НОВЫЙ builder!
                    for i in range(1, int(db_count_answer) + 1):
                        builder.button(text=f"Вариант {str(db_answer[i-1])}", callback_data=f"btn_{i}")
                    builder.adjust(1)
                    await msg.answer("Выберите ответ:", reply_markup=builder.as_markup())
                else:
                    await msg.answer("Введите свой ответ текстом:")

                answer = True
                found = True
                break

        db.close_db()

        if not found:
            await msg.answer("✅ Больше вопросов нет. Тест завершён.")
            start_test = False
            answer = False

    # === Сохраняем обновлённые данные пользователя ===
    users[user_index] = [user_id, start_press, takeFIO, start_test, answer, question, id_test, FIO, member, count_question]
    print("Обновлённые данные пользователя:", users[user_index])


# === Запуск бота ===
async def main():
    global bot
    bot = Bot(
        token='7728863257:AAFiNfCtlIDN-DN9IN6WyIMbTAo8lVF7lqI',
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

# === Точка входа ===
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())