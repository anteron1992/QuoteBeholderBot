import asyncio
from tabulate import tabulate
from os import getenv
from qbot.db.database import Database
from qbot.market.tinvest import Tinvest
from qbot.logger import logger
from qbot.helpers import path_db
from qbot.interval_actions import interval_polling, interval_news
from aiogram import Bot, Dispatcher, executor, types


tinkoff = Tinvest()
db = Database()

bot = Bot(token=getenv("TELE_TOKEN"))
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply(
        text=f"QuoteBeholder это бот, который информирует об резких изменениях котировок.\nУкажите команду после '/'",
    )
    db.add_new_user_to_db(message.chat.id, message.chat.first_name)


def subscribe(message: types.Message):
    if not db.check_user(message.from_user.id):
        await message.reply(f"Сначала нужно нажать /start"
        )
        return
    if message.get_args():
        sub_tickers = list()
        for ticker in message.get_args():
            if not db.check_ticker(ticker, message.from_user.id):
                try:
                    tinkoff.subscribe_ticker(
                        ticker,
                        message.from_user.username,
                        message.from_user.id
                    )
                    sub_tickers.append(ticker)
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
        if sub_tickers:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Вы успешно подписались на {', '.join(sub_tickers)}",
            )
    else:
        await message.reply("Не указаны тикеры, запустите команду так: /subscribe <TIK> или так /subscribe <TIK> <TIK> <TIK>",
        )
        return


def unsubscribe(message: types.Message):
    if not db.check_user(message.from_user.id):
        await message.reply(f"Сначала нужно нажать /start"
        )
        return
    if message.get_args():
        sub_tickers = list()
        for ticker in message.get_args():
            if db.check_ticker(ticker, message.from_user.id):
                db.delete_subscribed_ticker(
                    ticker,
                    message.from_user.username,
                    message.from_user.id
                )
                sub_tickers.append(ticker)
            else:
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"Тикер {ticker} не найден в подписке.",
                )
        if sub_tickers:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"{', '.join(sub_tickers)} удалены из подписки",
            )
    else:
        await message.reply("Не указаны тикеры, запустите команду так: /del_subscribe <TIK> или так /subscribe <TIK> <TIK> <TIK>",
        )
        return


def subscribe_pf(message: types.Message):
    if not db.check_user(message.from_user.id):
        await message.reply(f"Сначала нужно нажать /start"
        )
        return
    if message.get_args():
        await message.reply(f"Для этой функции недоступны аргументы, запустите её без них.",
        )
        return
    if message.from_user.id == 176549646:
        tinkoff.subscribe_portfolio(
            tinkoff.get_portfolio(message.from_user.id),
            message.from_user.username,
            message.from_user.id
        )
        await message.reply(f"Подписка на портфель оформлена"
        )
    else:
        await message.reply(f"Эта функция, к сожалению не доступна для вас.",
        )


def unsubscribe_pf(message: types.Message):
    if not db.check_user(message.from_user.id):
        await message.reply(f"Сначала нужно нажать /start"
        )
        return
    if message.get_args():
        await message.reply(f"Для этой функции недоступны аргументы, запустите её без них.",
        )
        return
    if message.from_user.id == 176549646:
        tinkoff.delete_subscribe_portfolio(
            tinkoff.get_portfolio(message.from_user.id),
            message.from_user.username,
            message.from_user.id
        )
        await message.reply(f"Подписка на портфель отключена"
        )
    else:
        await message.reply(f"Эта функция, к сожалению не доступна для вас.",
        )


def show_subscribe(message: types.Message):
    if not db.check_user(message.from_user.id):
        await message.reply(f"Сначала нужно нажать /start"
        )
        return
    header = ["Тикер", "Название"]
    if message.get_args():
        await message.reply(f"Для этой функции недоступны аргументы, запустите её без них.",
        )
        return
    subscribe_list = db.show_list_of_subscribes(message.from_user.username, message.from_user.id)
    if subscribe_list:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            parse_mode="Markdown",
            text=f"`{tabulate(subscribe_list, headers=header, tablefmt='pipe', stralign='left')}`",
        )
    else:
        await message.reply(f"Ваш список на подписку пуст. Добавьте что-нибудь при помощи /subscribe",
        )


def show_ticker(message: types.Message):
    if not db.check_user(message.from_user.id):
        await message.reply(f"Сначала нужно нажать /start"
        )
        return
    if message.get_args():
        for ticker in message.get_args():
            try:
                rez = tinkoff.show_brief_ticker_info_by_id(ticker, message.from_user.id)
            except ValueError:
                context.bot.send_message(
                    chat_id=update.effective_chat.id, text=f"Тикер {ticker} не найден."
                )
                return
            message = f"""*Тикер*: {rez['ticker']}
*Имя*: {rez['name']}
*Последняя цена*: {rez['last_price']}
*Текущаяя цена*: {rez['curr_price']}
*Разница*: {rez['diff']}
#{rez['link']}"""
            context.bot.send_message(
                chat_id=update.effective_chat.id, parse_mode="Markdown", text=message
            )
    else:
        await message.reply(f"Не указаны тикеры, запустите команду так: /show_ticker <TIK> или так /show_ticker <TIK> <TIK> <TIK>",
        )


def unknown(message: types.Message):
    logger.info(
        f"{message.from_user.username} ({message.from_user.id}) sent unknown command: {update.message.get_args()}"
    )
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Такой команды нет, выбери нужную команду из списка.",
    )


def unknown_text(message: types.Message):
    logger.info(
        f"{message.from_user.username} ({message.from_user.id}) sent unknown command: {update.message.get_args()}"
    )
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Допускаются только команды /.",
    )


start_handler = CommandHandler("start", start)
dispatcher.add_handler(start_handler)

subscribe_handler = CommandHandler("subscribe", subscribe)
dispatcher.add_handler(subscribe_handler)

subscribe_pf_handler = CommandHandler("subscribe_pf", subscribe_pf)
dispatcher.add_handler(subscribe_pf_handler)

del_subscribe_handler = CommandHandler("unsubscribe", unsubscribe)
dispatcher.add_handler(del_subscribe_handler)

del_subscribe_pf_handler = CommandHandler("unsubscribe_pf", unsubscribe_pf)
dispatcher.add_handler(del_subscribe_pf_handler)

show_subscribe_handler = CommandHandler("show_subscribe", show_subscribe)
dispatcher.add_handler(show_subscribe_handler)

show_ticker_handler = CommandHandler("show_ticker", show_ticker)
dispatcher.add_handler(show_ticker_handler)

unknown_command_handler = MessageHandler(
    Filters.command, unknown
)  # Если приходит команда, которую не знаем - пускаем функцию unknown
dispatcher.add_handler(unknown_command_handler)

unknown_text_handler = MessageHandler(
    Filters.text, unknown_text
)  # Отвечаем на любые не команды
dispatcher.add_handler(unknown_text_handler)


# async def main():
#    await asyncio.gather(interval_polling(), interval_news())


# def run ():
#    asyncio.new_event_loop().run_until_complete(main())


if __name__ == "__main__":
    # run()
    updater.start_polling()
    # print (db.check_user('176549646')) -> True

