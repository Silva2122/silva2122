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

    text = ""
    if not id:
        id = await db.get_id()
    else:
        text += "Записал в базу! "

    bot_username = (await bot.me).username
    bot_link = f"https://t.me/{bot_username}?start={id}"
    balance = await db.check_balance()
    text += f"""

Добро пожаловать в мир кривтовалюты CryptoChange

Нас уже {count_users} человек!

Подробнее о нас:
Наш чат: @cryptocommunicate


Администрация: 
@CryptoChangeSupport
@CryptoChangeAdmin

Ваша реферальная ссылка: {bot_link}

Проверить рефералов можно по команде: /referrals

Ваш бонусный баланс: {balance} монет.

"""

    await bot.send_message(chat_id, text)


@dp.message_handler(lambda message: "Курс обмена" == message.text)
async def btnl(message: types.Message):
    keyboard_markup = types.InlineKeyboardMarkup(row_width=3)
    keyboard_markup.add(
        types.InlineKeyboardButton('Наш Сайт', url='http://cryptochange.tilda.ws'),
    )
    text = f""
    text += f"""
<b>Курс обмена</b>

<i>В Нашей системе Вы можете ознакомится с перечнем криптовалют, обмен которых мы совершаем, а так же, помимо 
инвестирования, воспользоваться услугой конвертации валют.</i>

                              <b>Цена</b>      <b>Изм(24ч.)</b>

Bitcoin	          $7 544,71	     -8,68%				
Ethereum	        $160,56	      -7,73%				
XRP	                     $0,28	      -6,72%							
Litecoin	            $49,43	      -9,60%				
EOS	                     $2,76	      -5,80%								
Stellar	                 $0,06	      -7,34%				
TRON	                  $0,01	      -8,13%				



<b>Внимание , курс обмена обновляется ежедневно в 12:00 по Мск, следите за новостями!</b>

Чтобы выгодно и надёжно совершить обмен валюты, Вам необходимо перейти на Наш сайт, на котором будет предоставлена вся 
необходимая информация.
"""
    await message.answer(text, reply_markup=keyboard_markup)


@dp.message_handler(lambda message: "О Нас" == message.text)
async def btnl (message: types.Message):

    keyboard_markup = types.InlineKeyboardMarkup(row_width=3)
    keyboard_markup.add(
        types.InlineKeyboardButton('Наш Сайт', url='http://cryptochange.tilda.ws'),
    )
    text = f""
    text += f"""
   <b> О Нас </b>

Наш сервис занимается исключительно <b>обменом криптовалют.</b>

Вы можете прямо сейчас воспользоваться обменником. Простые и понятные правила, помогут без труда совершить необходимую операцию.

<i>Вам не потребуется тратить свое время на расчеты, так как Наша система справится с этой задачей с максимальной выгодой 
для Вас, стоит всего лишь написать консультанту и ввести сумму для продажи или покупки.</i>

<b>Почему мы открыли новую ветвь для инвестиций с Вашей стороны, и вознаграждения с Нашей ?</b>

Об обменнике CryptoChange с каждым днём узнаёт большее кол-во людей , и так как Наш рекламный бюджет ограничен , мы привлекаем инвесторов со стороны, для проведения большего потока операций. 

<b>Став частью Нас, Вы можете быть уверены в стабильности Вашего дохода.</b>

Администрация:
@CryptoChangeAdmin
@CryptoChangeSupport
"""
    await message.answer(text,reply_markup=keyboard_markup)


@dp.message_handler(lambda message:"Реклама" == message.text)
async def btnl (message: types.Message):
    text = f""
    text += f"""
   <b>Реклама</b>
<i>
В следствии того, что Наш обменник носит коммерческий характер, мы предлагаем Вам посотрудничать с Нами, оказывая услуги 
по размещению рекламы.</i>

Мы отказываем без причины в случаях если Реклама:

<b>1) Несёт мошеннический характер.</b>

<b>2) Нацелена на рекламу каких-либо проектов, подвергая в сомнения наших инвесторов.</b>

<b>3) Порнографического характера.</b>


В остальных случаях заявки на размещение рекламы будут одобрены нашей администрацией. 

<b>Стоимость рекламы фиксирована, 1 рекламный пост - 200₽. 

Срок размещения - 12 часов с момента публикации.</b> 

Вся информация вашего рекламного поста будет находится в закрепе нашего чата, так же рекламное объявление будет 
размещено в нашем боте.

<b>Рекламу можно разместить по системе бартера, т.е вы публикуетесь у нас, а мы - на Вашем канале, если посчитаем, что активность и аудитория для нас покажутся интересными.</b>

По вопросам рекламы и сотрудничеству обращайтесь : 
@CryptoChangeAdmin 
"""
    await message.answer(text)


@dp.message_handler(lambda message: "Заработать 25%" == message.text)
async def btnl ( message:types.Message):

    keyboard_markup = types.InlineKeyboardMarkup(row_width=3)
    keyboard_markup.add(
        types.InlineKeyboardButton('Оплата через QIWI', url='https://qiwi.com/payment/form/99?currency=RUB&extra[%27account%27]=+79516657576&extra[%27comment%27]='),
    )
    text = f""
    uid = types.User.get_current().id
    text += f"""
<b>Инвестировать на 5 дней</b>

Наш QIWI: +79516657576

<b>После успешного инвестирования, вся информация о транзакции будет предоставлена в канале @cryptochangemoney. 

Деньги будут выплачены автоматически по истечению 120 часов с момента пополнения. Вам вернётся депозит и 25% ввиде заработка на кошелёк.</b>

<b>ВНИМАНИЕ❗️</b>
<b>Минимальная сумма пополнения - 100₽.</b>

<b>Инвестировать вы можете, осуществив перевод на наш QIWI кошелёк, указав в комментарии свой уникальный код для 
идентификации вашей транзакции:</b>  {uid} 

<i>Ваш депозит, без введённого уникального кода - не засчитывается!</i>

При возникновении вопросов немедленно обращайтесь в службу поддержки.
    """
    await bot.send_message(uid, text, reply_markup=keyboard_markup)


@dp.message_handler(lambda message: "Заработать 10%" == message.text)
async def btnl (message:types.Message):

    keyboard_markup = types.InlineKeyboardMarkup(row_width=3)
    keyboard_markup.add(
        types.InlineKeyboardButton('Оплата через QIWI', url='https://qiwi.com/payment/form/99?currency=RUB&extra[%27account%27]=+77056975701&extra[%27comment%27]='),
    )
    text = f""
    uid = types.User.get_current().id
    text += f"""
<b>Инвестировать на 3 дня</b>

Наш QIWI: +77056975701

<b>После успешного инвестирования, вся информация о транзакции будет предоставлена в канале @cryptochangemoney 

Деньги будут выплачены автоматически по истечению 120 часов с момента пополнения. Вам вернётся депозит и 10% ввиде заработка на кошелёк.</b>

<b>ВНИМАНИЕ❗️</b>
<b>Минимальная сумма пополнения - 100₽.</b>

<b>Инвестировать вы можете, осуществив перевод на наш QIWI кошелёк, указав в комментарии свой уникальный код для 
идентификации вашей транзакции:</b>  {uid} 

<i>Ваш депозит, без введённого уникального кода - не засчитывается!</i>

При возникновении вопросов немедленно обращайтесь в службу поддержки.
    """

    await bot.send_message(uid, text, reply_markup=keyboard_markup)


@dp.message_handler(lambda message: "Партнерская программа" == message.text)
async def btnl(message: types.Message):

    text = ""
    text += f"""Партнерская программа

<b>Уважаемый инвестор! Мы рады приветствовать Тебя в боте нашего обменника криптовалюты. 
Предлагаем Вам принять участие в реферальной программе и получить дополнительный доход.</b>

<i>Пригласив в систему нового участника, Вы получите определенный процент от депозита приглашенного пользователя, потому что он автоматически становится Вашим рефералом.</i>

Начисление реферального вознаграждения происходит по следующей схеме:

<b>Будет начислятся вознаграждение ввиде 3% от общей суммы депозитов, к ним относят участников системы, которых пригласили лично Вы.</b>

<b>Начисления по реферальной программе можно вывести, если у Вас есть как минимум 10 активных рефералов и если у каждого из 
них есть хоты бы одно успешное инвестирование.</b>

<i>Администрация в праве отказать в выплате реферальных вознаграждений и заблокировать аккаунт в случае выявления факта 
создание аккаунта от своего имени, т.е. в случаях когда оба аккаунат фактически зарегистрированы одним человеком.</i>
  
    
<b>Узнать вашу реферальную ссылку можно по команде:</b> /start

<b>Проверить колличество рефералов можно по команде:</b> /referrals
    """""
    await message.answer(text)


@dp.message_handler(commands=["referrals"])
async def check_referrals(message: types.Message):
    referrals = await db.check_referrals()
    text = f"Ваши рефералы:\n{referrals}"
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
    text = "Добро пожаловать в мир криптовалюты!"
    keyboard = ListOfButtons(
           text=["Заработать 10%%", "Заработать 25%", "Курс обмена", "Реклама", "Партнерская программа", "О Нас"],
           align=[2, 2, 1, 1]
    ).reply_keyboard
    await message.answer(text=text, reply_markup=keyboard)

