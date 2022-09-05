from os import getenv
from tabulate import tabulate
from aiogram import Bot, Dispatcher, types
from qbot.logger import logger
from qbot.app.application import application

bot = Bot(token=getenv("TELE_TOKEN"))
dp = Dispatcher(bot)
app = application()


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply(
        "QuoteBeholder это бот, который информирует об резких изменениях котировок.\nУкажите команду после '/'",
    )
    await app.db.add_new_user_to_db(message.from_user.id, message.from_user.username)


@dp.message_handler(commands=['subscribe'])
async def subscribe(message: types.Message):
    if not await app.db.check_user(message.from_user.id):
        await message.reply("Сначала нужно нажать /start")
    if message.get_args():
        sub_tickers = list()
        for ticker in message.get_args().split():
            if not await app.db.check_ticker(ticker, message.from_user.id):
                try:
                    await app.market['tinkoff'].subscribe_ticker(
                        ticker,
                        message.from_user.username,
                        message.from_user.id
                    )
                    sub_tickers.append(ticker)
                except ValueError:
                    await message.reply(f"Тикер {ticker} не найден.")
            else:
                await message.reply(f"Вы уже подписаны на тикер {ticker} .")
        if sub_tickers:
            await message.reply(f"Вы успешно подписались на {', '.join(sub_tickers)}")
    else:
        await message.reply(
            "Не указаны тикеры, запустите команду так: /subscribe <TIK> или так /subscribe <TIK> <TIK> <TIK>",
        )


@dp.message_handler(commands=['unsubscribe'])
async def unsubscribe(message: types.Message):
    if not await app.db.check_user(message.from_user.id):
        await message.reply("Сначала нужно нажать /start")
        return
    if message.get_args():
        sub_tickers = list()
        for ticker in message.get_args().split():
            if await app.db.check_ticker(ticker, message.from_user.id):
                await app.db.delete_subscribed_ticker(
                    ticker,
                    message.from_user.username,
                    message.from_user.id
                )
                sub_tickers.append(ticker)
            else:
                await message.reply(f"Тикер {ticker} не найден в подписке.")
        if sub_tickers:
            await message.reply(f"{', '.join(sub_tickers)} удалены из подписки")
    else:
        await message.reply(
            "Не указаны тикеры, запустите команду так: /del_subscribe <TIK> или так /subscribe <TIK> <TIK> <TIK>")


@dp.message_handler(commands=['subscribe_portfolio'])
async def subscribe_portfolio(message: types.Message):
    if not await app.db.check_user(message.from_user.id):
        await message.reply("Сначала нужно нажать /start")
        return
    if message.get_args().split():
        await message.reply("Для этой функции недоступны аргументы, запустите её без них.")
        return
    # TODO: Сделать функцию публичной для других людей
    if message.from_user.id == 176549646:
        await app.market['tinkoff'].subscribe_portfolio(
            app.market['tinkoff'].get_portfolio(message.from_user.id),
            message.from_user.username,
            message.from_user.id
        )
        await message.reply(f"Подписка на портфель оформлена")
    else:
        await message.reply(f"Эта функция, к сожалению не доступна для вас.")


@dp.message_handler(commands=['unsubscribe_portfolio'])
async def unsubscribe_portfolio(message: types.Message):
    if not await app.db.check_user(message.from_user.id):
        await message.reply(f"Сначала нужно нажать /start")
        return
    if message.get_args().split():
        await message.reply(f"Для этой функции недоступны аргументы, запустите её без них.")
        return
    if message.from_user.id == 176549646:
        await app.market['tinkoff'].delete_subscribe_portfolio(
            app.market['tinkoff'].get_portfolio(message.from_user.id),
            message.from_user.username,
            message.from_user.id
        )
        await message.reply("Подписка на портфель отключена")
    else:
        await message.reply("Эта функция, к сожалению не доступна для вас.")


@dp.message_handler(commands=['show_subscribes'])
async def show_subscribes(message: types.Message):
    if not await app.db.check_user(message.from_user.id):
        await message.reply("Сначала нужно нажать /start")
        return
    if message.get_args():
        await message.reply(f"Для этой функции недоступны аргументы, запустите её без них.")
        return
    header = ["Тикер", "Название"]
    subscribe_list = await app.db.show_list_of_subscribes(message.from_user.username, message.from_user.id)
    if subscribe_list:
        await message.reply(
            f"`{tabulate(subscribe_list, headers=header, tablefmt='pipe', stralign='left')}`",
            parse_mode="Markdown"
        )
    else:
        await message.reply("Ваш список на подписку пуст. Добавьте что-нибудь при помощи /subscribe")


@dp.message_handler(commands=['show_ticker'])
async def show_ticker(message: types.Message):
    # TODO: Сделать дефолт для тикеров не добавленных в портфель
    if not await app.db.check_user(message.from_user.id):
        await message.reply("Сначала нужно нажать /start")
        return
    if message.get_args():
        for ticker in message.get_args().split():
            try:
                rez = await app.market['tinkoff'].show_brief_ticker_info_by_id(ticker, message.from_user.id)
            except ValueError:
                await message.reply(f"Тикер {ticker} не найден.")
                return
            msg = (
                f"*Тикер*: {rez['ticker']}\n"
                f"*Имя*: {rez['name']}\n"
                f"*Последняя цена*: {rez['last_price']}\n"
                f"*Текущаяя цена*: {rez['curr_price']}\n"
                f"*Разница*: {rez['diff']}"
            )
            await message.reply(msg, parse_mode="Markdown")
    else:
        await message.reply(
            "Не указаны тикеры, запустите команду так: /show_ticker <TIK> или так /show_ticker <TIK> <TIK> <TIK>"
        )


@dp.message_handler()
async def unknown(message: types.Message):
    logger.info(
        f"{message.from_user.username} ({message.from_user.id}) sent unknown command: {message.get_args()}"
    )
    if message.get_args().startswith("/"):
        await message.reply("Такой команды нет, выбери нужную команду из списка.")
    else:
        await message.reply("Допускаются только команды /")
