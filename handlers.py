import random
from aiogram import types
from asyncpg import Connection, Record
from asyncpg.exceptions import UniqueViolationError
from load_all import bot, dp, db

from keyboards import ListOfButtons


class DBCommands:

    pool: Connection = db
    ADD_NEW_USER_REFERRAL = "INSERT INTO users(chat_id, username, full_name, referral) " \
                            "VALUES ($1, $2, $3, $4) RETURNING id"
    ADD_NEW_USER = "INSERT INTO users(chat_id, username, full_name) VALUES ($1, $2, $3) RETURNING id"
    COUNT_USERS = "SELECT COUNT(*) FROM users"
    GET_ID = "SELECT id FROM users WHERE chat_id = $1"
    CHECK_REFERRALS = "SELECT chat_id FROM users WHERE referral=" \
                      "(SELECT id FROM users WHERE chat_id=$1)"
    CHECK_BALANCE = "SELECT balance FROM users WHERE chat_id = $1"
    ADD_MONEY = "UPDATE users SET balance=balance+$1 WHERE chat_id = $2"

    async def add_new_user(self, referral=None):
        user = types.User.get_current()

        chat_id = user.id
        username = user.username
        full_name = user.full_name
        args = chat_id, username, full_name

        if referral:
            args += (int(referral),)
            command = self.ADD_NEW_USER_REFERRAL
        else:
            command = self.ADD_NEW_USER

        try:
            record_id = await self.pool.fetchval(command, *args)
            return record_id
        except UniqueViolationError:
            pass

    async def count_users(self):
        record: Record = await self.pool.fetchval(self.COUNT_USERS)
        return record

    async def get_id(self):
        command = self.GET_ID
        user_id = types.User.get_current().id
        return await self.pool.fetchval(command, user_id)

    async def check_referrals(self):
        user_id = types.User.get_current().id
        command = self.CHECK_REFERRALS
        rows = await self.pool.fetch(command, user_id)
        return ", ".join([
            f"{num + 1}. " + (await bot.get_chat(user["chat_id"])).get_mention(as_html=True)
            for num, user in enumerate(rows)
        ])

    async def check_balance(self):
        command = self.CHECK_BALANCE
        user_id = types.User.get_current().id
        return await self.pool.fetchval(command, user_id)

    async def add_money(self, money):
        command = self.ADD_MONEY
        user_id = types.User.get_current().id
        return await self.pool.fetchval(command, money, user_id)


db = DBCommands()


@dp.message_handler(commands=["start"])
async def register_user(message: types.Message):
    chat_id = message.from_user.id
    referral = message.get_args()
    id = await db.add_new_user(referral=referral)
    count_users = await db.count_users()
    keyboard = ListOfButtons(
        text=["Стать предпринимателем 💼", "Пригласить члена партии 🗣", "Все о партии 🌍", "Общение ☎️", "Социальная иерархия СССР 🇲🇪"],
        align=[2, 2, 1]
    ).reply_keyboard
    text = "Добро пожаловать, коммунист!"
    if not id:
        id = await db.get_id()
    else:
        text += "Записал в базу! "

    bot_username = (await bot.me).username
    bot_link = f"https://t.me/{bot_username}?start={id}"
    balance = await db.check_balance()
    text += f"""

<b>Мы видим, что ты заблудился и находишься в поисках нужного пути для дальнейшего движения по просторам интернета.</b> 

Тебе однозначно повезло! Если ты читаешь данное послание, то уже мысленно вступил в партию Коммуналка СССР. 
Последний шаг за тобой. Действуй. Чего же ты ждёшь?
<b>Мы рады тебя приветствовать в нашей партии.</b>

"""

    await bot.send_message(chat_id, text, reply_markup=keyboard)


@dp.message_handler(lambda message: "Социальная иерархия СССР 🇲🇪" == message.text)
async def btnl(message: types.Message):
    keyboard_markup = types.InlineKeyboardMarkup(row_width=3)
    keyboard_markup.add(
        types.InlineKeyboardButton('Структура партии 🏰', url='https://telegra.ph/Struktura-partii-11-11'),
    )
    text = f""
    text += f"""Социальная иерархия СССР 🇲🇪

<b>В каждой партии для полноценности работы существует иерархия, с помощью которой осуществляется надзор за исполнением надлежащих обязанностей.</b>

Каждый член партии имеет право на получение должности в нашей коммуне. 

<b>Любой труд должен быть оплачен, в связи с этим, каждая должность будет приносить однопартийцам дополнительные дивиденды.</b>

За покупкой, обращайтесь к Лаврентию Павловичу: @beriaCCCP
"""
    await message.answer(text, reply_markup=keyboard_markup)


@dp.message_handler(lambda message: "Общение ☎️" == message.text)
async def btnl(message: types.Message):
    keyboard_markup = types.InlineKeyboardMarkup(row_width=3)
    keyboard_markup.add(
        types.InlineKeyboardButton('Наш чат 🎬', url='t.me/communistchat'),
    )
    keyboard_markup.add(
        types.InlineKeyboardButton('Глава партии 🧠', url='t.me/GeneralStalinBot'),
    )
    text = f""
    text += f"""

Общение ☎

Легко и просто всегда оставаться на связи со своими однопартийцами и получить поддержку от главы партии. 

<b>Внизу размещены кнопки на наш чат и Генерального секретаря ЦК КПСС</b>

<b>Честный розыгрыш :</b>

Дорогие товарищи! 
Каждый член партии имеет право получить талон для участия в партийной лотерее ( по принципу : один талон в одни руки ).

В конце рабочей недели, каждую пятницу в 18:00 будет проходить лотерея на случайную сумму, которую будет разыгрывать глава партии. 
Победителей может быть как один, так и несколько, в зависимости от количества участников. 

<b>Ближайшие конкурсы в нашем чате:</b>
Загадки в чате. Главный приз - 1500 RUB Дата 15.11.2019

Всем желаем удачи, честных побед и приятного времяпровождения.
"""
    await message.answer(text, reply_markup=keyboard_markup)


@dp.message_handler(lambda message: "Все о партии 🌍" == message.text)
async def btnl (message: types.Message):

    text = f""
    text += f"""
   Все о партии 🌍

<b>Простейший факт: Коммунистические лидеры очень богаты.</b>

<i>Да, несмотря на декларируемое стремление к социальной справедливости и показушную скромность, лидеры коммунистов никогда не жили так же, как народ.
Мы, от лица данной партии хотим, чтобы каждый из Вас не отказывал себе в необходимых потребностях. </i> 

<b>Почему коммунисты так быстро уходят со сцены?</b>

<i>Отвечаем: Невозможно заниматься разрушением долгое время. Ведь когда-то должно закончиться, исчерпаться то, что можно делить и перераспределять, ничего при этом не создавая.

Инвестиционный проект</i> <b>Коммуналка СССР</b> <i>предлагает каждому задержаться на сцене, оказаться лидером, начать 
мыслить нестандартно, а так же, создать достойный капитал для реализации своих желаний.</i>

<b>Главный вопрос, пожалуй, интересующий каждого члена партии. Откуда же берутся финансы, с помощью которых существует партия?</b>

<i>Так как в нашем уставе партии прописано, что вся информация о доходах является конфиденциальной, мы не будем раскрывать весь смысл заработка. 
Однако что-то мы от Вас не утоим.</i> 

<b>Коммуналка СССР</b> выявляет различные финансовые проекты , с помощью которых можно увеличить оборот Нашей коммуны. 
Вы смело можете быть уверены в завтрашнем дне. Одна из главных заповедей партии гласит 

<b>«Коллективизм и товарищеская помощь превыше всего, один за всех, все за одного!»</b>

"""
    await message.answer(text)


@dp.message_handler(lambda message: "Стать предпринимателем 💼" == message.text)
async def btnl ( message:types.Message):

    keyboard_markup = types.InlineKeyboardMarkup(row_width=3)
    keyboard_markup.add(
        types.InlineKeyboardButton('Оплата через QIWI', url='https://qiwi.com/payment/form/99?currency=RUB&extra[%27account%27]=+77056975701&extra[%27comment%27]='),
    )
    text = f""
    uid = types.User.get_current().id
    text += f"""
Стать предпринимателем 💼

<b>Предприниматели, подогреваемые своей жадностью, очень сильно переоценивали свой вклад в процесс.</b> 

Нужно чётко понимать, что на данном этапе, пока материальных благ не будет в полном достатке, обратная связь ввиде прибыли является пропорциональной. 
Став частью Коммуналки СССР, уделив минимальные усилия. 

<b>Вы сможете иметь 20% дохода ввиде дивидендов, впоследствии которые можно потратить на реализацию своих желаний.</b> 

<b>QIWI Кошелёк для пополнения:</b> +77056975701

<b>Инвестировать вы можете, осуществив перевод на наш QIWI кошелёк, указав в комментарии свой уникальный код для 
идентификации вашей транзакции:</b>  {uid} 

Так как прибыль будет получена Вами сразу, то полное право на её распоряжение остаётся за Вами. Основной вклад явится обратно в течение 5 суток. 

<i>Ваш депозит, без введённого уникального кода - не засчитывается!</i>

<b>Своё пополнение в копилку партии Вы можете отследить здесь: @ussrpay</b>

<b>При возникновении вопросов немедленно обращайтесь в службу поддержки.</b>
    """
    await bot.send_message(uid, text, reply_markup=keyboard_markup)


@dp.message_handler(lambda message: "Пригласить члена партии 🗣" == message.text)
async def btnl(message: types.Message):
    chat_id = message.from_user.id
    referral = message.get_args()
    id = await db.add_new_user(referral=referral)
    text = "Всем доброго дня!"
    if not id:
        id = await db.get_id()
    else:
        text += "Записал в базу! "

    bot_username = (await bot.me).username
    bot_link = f"https://t.me/{bot_username}?start={id}"
    text = ""
    text += f"""Пригласить члена партии 🗣

<b>Мы ценим ваши старания. Мы работаем над Собой и стараемся сделать Вас более независимым.</b> 

Увеличить материальные блага можно очень просто: за каждого приглашённого Вами нового члена партии будет выставлено вознаграждение, ввиде 5% от его первого пополнения. 

<b>Партийные выплаты осуществляются строго во вторник каждые две недели с 16:00-21:00.</b>

Ваша партийная ссылка: {bot_link}
При любых трудностях обращайтесь к главе партии: @GeneralStalinBot
  
<b>Проверить колличество рефералов можно по команде:</b> /communal
    """""
    await bot.send_message(chat_id, text)


@dp.message_handler(commands=["communal"])
async def check_referrals(message: types.Message):
    referrals = await db.check_referrals()
    text = f"Ваши однопартийцы:\n{referrals}"
    await message.answer(text)


@dp.message_handler(commands=["add_money"])
async def add_money(message: types.Message):
    random_amount = random.randint(1, 100)
    await db.add_money(random_amount)
    balance = await db.check_balance()

    text = f"""
Вам было добавлено {random_amount} монет.
Теперь ваш баланс: {balance}
    """
    await message.answer(text)


@dp.message_handler()
async def keyboards(message: types.Message):
    text = "Добро пожаловать, коммунист!"
    keyboard = ListOfButtons(
           text=["Стать предпринимателем 💼", "Пригласить члена партии 🗣", "Все о партии 🌍", "Общение ☎️", "Социальная иерархия СССР 🇲🇪"],
           align=[2, 2, 1]
    ).reply_keyboard
    await message.answer(text=text, reply_markup=keyboard)

