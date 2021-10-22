from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    InlineQueryHandler,
)
from telegram.ext.dispatcher import run_async
from telegram import InlineQueryResultArticle, InputTextMessageContent, ParseMode, Bot
from openapi_client import openapi
from auth import TELE_TOKEN, SAND_TOKEN
from time import sleep
from tabulate import tabulate
from os import path
from math import fabs
from openapi_genclient import exceptions
import html
import json
import traceback
import requests
import asyncio
import sqlite3
import create_db
import logging

INTERVAL = 3600
PERCENT = 2.0
logging.basicConfig(
    filename="/var/log/quotebeholder.log",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
create_db.conndb()
client = openapi.api_client(SAND_TOKEN)
updater = Updater(token=TELE_TOKEN)
dispatcher = updater.dispatcher
sender = Bot(token=TELE_TOKEN)
pf = client.portfolio.portfolio_get().to_dict()
URL = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
TRIES = 5

def search_ticker(ticker):
    try:
        return client.market.market_search_by_ticker_get(ticker)
    except exceptions.ApiException as expt:
        if TRIES == 0:
            logging.CRITICAL("Не удалось соединиться :(")
            raise ConnectionError
        logging.ERROR(expt)
        logging.WARNING("Пытаюсь установить соединение снова. Попытка {TRIES}...")
        TRIES -= 1
        sleep(5)
        search_ticker(ticker)


def check_ticker_in_db(ticker, user):
    connect = sqlite3.connect(create_db.DB_NAME)
    row = (user.effective_user.id, ticker.upper())
    try:
        with connect:
            query = "SELECT ticker FROM tickers WHERE id=? AND ticker=?"
            return [line for line in connect.execute(query, row)]
    except sqlite3.IntegrityError:
        pass


def add_new_user_to_db(user):
    connect = sqlite3.connect(create_db.DB_NAME)
    row = (user.effective_user.id, user.effective_user.name)
    try:
        with connect:
            query = "INSERT INTO usernames VALUES (?, ?, datetime('now'))"
            connect.execute(query, row)
    except sqlite3.IntegrityError:
        pass


def subscribe_on_new_ticker(ticker, user):
    tk = search_ticker(ticker).to_dict()
    connect = sqlite3.connect(create_db.DB_NAME)
    if tk["payload"]["instruments"]:
        if not check_ticker_in_db(ticker, user):
            ticker = tk["payload"]["instruments"][0]["ticker"]
            name = tk["payload"]["instruments"][0]["name"]
            price = client.market.market_orderbook_get(
                tk["payload"]["instruments"][0]["figi"], 3
            ).to_dict()["payload"]["last_price"]
            row = (
                user.effective_user.id,
                user.effective_user.name,
                ticker,
                name,
                price,
            )
            try:
                with connect:
                    query = "INSERT INTO tickers VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'))"
                    connect.execute(query, row)
            except sqlite3.IntegrityError:
                pass
    # Если будет всё ок, выпилить это недоразумение
    #    else:
    #        sender.sendMessage(chat_id=user.effective_chat.id, parse_mode=ParseMode.HTML, text="Тикер {ticker} уже добавлен")
    else:
        raise ValueError(f"Тикер {ticker} не найден")


def del_subscribe_on_new_ticker(ticker, user):
    connect = sqlite3.connect(create_db.DB_NAME)
    row = (user.effective_user.id, ticker.upper())
    try:
        with connect:
            query = "DELETE FROM tickers WHERE id=? AND ticker=?;"
            connect.execute(query, row)
    except sqlite3.IntegrityError:
        pass


def subscribe_portfolio(pf, user):
    for pos in pf["payload"]["positions"]:
        subscribe_on_new_ticker(pos["ticker"], user)


def del_subscribe_portfolio(pf, user):
    for pos in pf["payload"]["positions"]:
        del_subscribe_on_new_ticker(pos["ticker"], user)


def show_list_of_subscribes(user):
    row = (user.effective_user.id,)
    connect = sqlite3.connect(create_db.DB_NAME)
    try:
        with connect:
            query = f"SELECT ticker, name FROM tickers WHERE id=?;"
            return connect.execute(query, row).fetchall()
    except sqlite3.IntegrityError:
        pass


def show_list_of_subscribes_by_id(id):
    row = (id,)
    connect = sqlite3.connect(create_db.DB_NAME)
    try:
        with connect:
            query = f"SELECT ticker FROM tickers WHERE id=?"
            return connect.execute(query, row).fetchall()
    except sqlite3.IntegrityError:
        pass


def show_usernames_from_db():
    connect = sqlite3.connect(create_db.DB_NAME)
    try:
        with connect:
            query = "SELECT id FROM usernames;"
            return connect.execute(query).fetchall()
    except sqlite3.IntegrityError:
        pass


def count_percent(last_price, new_price):
    return normalize_float(
        (float(new_price) - float(last_price)) / (float(last_price) / 100)
    )


def normalize_float(value):
    return "{0:.2f}".format(float(value))


def show_ticker_info(ticker, user):
    tk = search_ticker(ticker).to_dict()
    row = (user.effective_user.id, ticker.upper())
    connect = sqlite3.connect(create_db.DB_NAME)
    if tk["payload"]["instruments"]:
        price = client.market.market_orderbook_get(
            tk["payload"]["instruments"][0]["figi"], 3
        ).to_dict()["payload"]["last_price"]
        query = "SELECT * FROM tickers WHERE id=? AND ticker=?;"
        try:
            with connect:
                result = connect.execute(query, row).fetchall()[0]
                return {
                    "ticker": result[2],
                    "name": result[3],
                    "last_price": result[4],
                    "curr_price": price,
                    "diff": str(count_percent(result[4], price)) + "%",
                    "link": "https://bcs-express.ru/kotirovki-i-grafiki/" + ticker,
                }
        except (sqlite3.IntegrityError, sqlite3.OperationalError, IndexError):
            return {
                "ticker": tk["payload"]["instruments"][0]["ticker"],
                "name": tk["payload"]["instruments"][0]["name"],
                "last_price": "Тикер не добавлен в подписки",
                "curr_price": price,
                "diff": "Тикер не добавлен в подписки",
                "link": "https://bcs-express.ru/kotirovki-i-grafiki/"
                + tk["payload"]["instruments"][0]["ticker"],
            }
    else:
        raise ValueError(f"Тикер {ticker} не найден")


def show_ticker_info_by_id(ticker, id):
    row = (id, ticker.upper())
    tk = search_ticker(ticker).to_dict()
    connect = sqlite3.connect(create_db.DB_NAME)
    if tk["payload"]["instruments"]:
        price = client.market.market_orderbook_get(
            tk["payload"]["instruments"][0]["figi"], 3
        ).to_dict()["payload"]["last_price"]
        query = "SELECT * FROM tickers WHERE id=? AND ticker=?;"
        try:
            with connect:
                result = connect.execute(query, row).fetchall()[0]
                return {
                    "ticker": result[2],
                    "last_price": result[4],
                    "curr_price": price,
                    "diff": float(count_percent(result[4], price)),
                }
        except (sqlite3.IntegrityError, sqlite3.OperationalError, IndexError):
            pass


def check_user_in_db(user):
    row = (user.effective_user.id,)
    connect = sqlite3.connect(create_db.DB_NAME)
    try:
        with connect:
            query = f"SELECT * FROM usernames WHERE id=?;"
            if str(user.effective_user.id) in connect.execute(query, row).fetchall():
                return True
            else:
                return connect.execute(query, row).fetchall()
    except (sqlite3.IntegrityError, sqlite3.OperationalError):
        return connect.execute(query, row).fetchall()


def override_price(id, ticker_info):
    row = (ticker_info["curr_price"], id, ticker_info["ticker"])
    connect = sqlite3.connect(create_db.DB_NAME)
    try:
        with connect:
            query = "UPDATE tickers SET price=?, updated=datetime('now') WHERE id=? AND ticker=?;"
            connect.execute(query, row)
    except sqlite3.IntegrityError:
        pass


#######################################TELEGRAM FUNCTIONS##########################################################


def start(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="QuoteBeholder это бот, который информирует об резких изменениях котировок.\nУкажите команду после '/'",
    )
    add_new_user_to_db(update)


def subscribe(update, context):
    if not check_user_in_db(update):
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=f"Сначала нужно нажать /start"
        )
        return
    if context.args:
        sub_tikers = list()
        for ticker in context.args:
            if not check_ticker_in_db(ticker, update):
                try:
                    subscribe_on_new_ticker(ticker, update)
                    sub_tikers.append(ticker)
                except ValueError:
                    context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=f"Тикер {ticker} не найден.",
                    )
            else:
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"Вы уже подписаны на тикер {ticker} .",
                )
        if sub_tikers:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Вы успешно подписались на {', '.join(sub_tikers)}",
            )
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Не указаны тикеры, запустите команду так: /subscribe <TIK> или так /subscribe <TIK> <TIK> <TIK>",
        )
        return


def subscribe_pf(update, context):
    if not check_user_in_db(update):
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=f"Сначала нужно нажать /start"
        )
        return
    if context.args:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Для этой функции недоступны аргументы, запустите её без них.",
        )
        return
    if update.effective_user.id == 176549646:
        subscribe_portfolio(pf, update)
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=f"Подписка на портфель оформлена"
        )
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Эта функция, к сожалению не доступна для вас.",
        )


def del_subscribe(update, context):
    if not check_user_in_db(update):
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=f"Сначала нужно нажать /start"
        )
        return
    if context.args:
        sub_tikers = list()
        for ticker in context.args:
            if check_ticker_in_db(ticker, update):
                del_subscribe_on_new_ticker(ticker, update)
                sub_tikers.append(ticker)
            else:
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"Тикер {ticker} не найден в подписке.",
                )
        if sub_tikers:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"{', '.join(sub_tikers)} удалены из подписки",
            )
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Не указаны тикеры, запустите команду так: /del_subscribe <TIK> или так /subscribe <TIK> <TIK> <TIK>",
        )
        return


def del_subscribe_pf(update, context):
    if not check_user_in_db(update):
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=f"Сначала нужно нажать /start"
        )
        return
    if context.args:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Для этой функции недоступны аргументы, запустите её без них.",
        )
        return
    if update.effective_user.id == 176549646:
        del_subscribe_portfolio(pf, update)
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=f"Подписка на портфель отключена"
        )
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Эта функция, к сожалению не доступна для вас.",
        )


def show_subscribe(update, context):
    if not check_user_in_db(update):
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=f"Сначала нужно нажать /start"
        )
        return
    header = ["Тикер", "Название"]
    if context.args:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Для этой функции недоступны аргументы, запустите её без них.",
        )
        return
    if show_list_of_subscribes(update):
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            parse_mode="Markdown",
            text=f"`{tabulate(show_list_of_subscribes(update), headers=header, tablefmt='pipe', stralign='left')}`",
        )
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Ваш список на подписку пуст. Добавьте что-нибудь при помощи /subscribe",
        )


def show_ticker(update, context):
    if not check_user_in_db(update):
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=f"Сначала нужно нажать /start"
        )
        return
    if context.args:
        for ticker in context.args:
            try:
                rez = show_ticker_info(ticker, update)
            except ValueError:
                context.bot.send_message(
                    chat_id=update.effective_chat.id, text=f"Тикер {ticker} не найден."
                )
            message = f"""*Тикер*: {rez['ticker']}
*Имя*: {rez['name']}
*Последняя цена*: {rez['last_price']}
*Текущаяя цена*: {rez['curr_price']}
*Разница*: {rez['diff']}
{rez['link']}
            """
            context.bot.send_message(
                chat_id=update.effective_chat.id, parse_mode="Markdown", text=message
            )
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Не указаны тикеры, запустите команду так: /show_ticker <TIK> или так /show_ticker <TIK> <TIK> <TIK>",
        )


async def interval_polling():
    flag = True
    polling_list = dict()
    users_table = show_usernames_from_db()
    while True:
        for line in users_table:
            polling_list.update({line[0]: show_list_of_subscribes_by_id(line[0])})
        for id in polling_list:
            for ticker in polling_list[id]:
                rez = show_ticker_info_by_id(ticker[0], id)
                if fabs(rez["diff"]) >= PERCENT:
                    flag = False
                    tik = rez["ticker"]
                    diff = rez["diff"]
                    message = f"<a href='https://bcs-express.ru/kotirovki-i-grafiki/{tik}'>{tik}</a> {diff}%"
                    if rez["diff"] > 0:
                        message = f"<a href='https://bcs-express.ru/kotirovki-i-grafiki/{tik}'>{tik}</a> +{diff}%"
                    sender.sendMessage(
                        chat_id=id, parse_mode=ParseMode.HTML, text=message
                    )
                    logging.info(
                        f"Цена на тикер {rez['ticker']} изменилась на {rez['diff']}% cообщение отправлено на {id} сообщение: \n{message}"
                    )
                    override_price(id, rez)
        await asyncio.sleep(INTERVAL)


def unknown(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Такой команды нет, выбери нужную команду из списка.",
    )

def error_handler(update, context):
    logging.ERROR("Возникла ошибка {context.error}")
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = ''.join(tb_list)
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
    f'Возникло исключение при обработке сообщения.\n'
    f'<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}'
    '</pre>\n\n'
    f'<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n'
    f'<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n'
    f'<pre>{html.escape(tb_string)}</pre>')
    context.bot.send_message(chat_id=176549646, text=message, parse_mode=ParseMode.HTML)

start_handler = CommandHandler("start", start)
dispatcher.add_handler(start_handler)

subscribe_handler = CommandHandler("subscribe", subscribe)
dispatcher.add_handler(subscribe_handler)

subscribe_pf_handler = CommandHandler("subscribe_pf", subscribe_pf)
dispatcher.add_handler(subscribe_pf_handler)

del_subscribe_handler = CommandHandler("del_subscribe", del_subscribe)
dispatcher.add_handler(del_subscribe_handler)

del_subscribe_pf_handler = CommandHandler("del_subscribe_pf", del_subscribe_pf)
dispatcher.add_handler(del_subscribe_pf_handler)

show_subscribe_handler = CommandHandler("show_subscribe", show_subscribe)
dispatcher.add_handler(show_subscribe_handler)

show_ticker_handler = CommandHandler("show_ticker", show_ticker)
dispatcher.add_handler(show_ticker_handler)

unknown_handler = MessageHandler(
    Filters.command, unknown
)  # Если приходит команда, которую не знаем - пускаем функцию unknown
dispatcher.add_handler(unknown_handler)
# Обработчик ошибок
dispatcher.add_error_handler(error_handler)

if __name__ == "__main__":
    updater.start_polling()
    try:
        asyncio.new_event_loop().run_until_complete(interval_polling())
    except Exception as e:
        logging.exception("Exception: %r", e)
