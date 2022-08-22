import asyncio
from tabulate import tabulate
from qbot.telebot.telebot import Telegram
from qbot.db.database import Database
from qbot.market.tinvest import Tinvest
from qbot.logger import logger
from qbot.interval_actions import interval_polling, interval_news
from telegram.ext import (
    CommandHandler,
    MessageHandler,
)

tinkoff = Tinvest()
telegram = Telegram()
db = Database()


@telegram.deploy(handler=CommandHandler)
def start(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="QuoteBeholder это бот, который информирует об резких изменениях котировок.\nУкажите команду после '/'",
    )
    db.add_new_user_to_db(update.effective_user.id, update.effective_user.name)


@telegram.deploy(handler=CommandHandler)
def subscribe(update, context):
    if not db.check_user(update.effective_user.id):
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=f"Сначала нужно нажать /start"
        )
        return
    if context.args:
        sub_tickers = list()
        for ticker in context.args:
            if not db.check_ticker(ticker, update.effective_user.id):
                try:
                    tinkoff.subscribe_ticker(
                        ticker,
                        update.effective_user.name,
                        update.effective_user.id
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
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Не указаны тикеры, запустите команду так: /subscribe <TIK> или так /subscribe <TIK> <TIK> <TIK>",
        )
        return


@telegram.deploy(handler=CommandHandler)
def unsubscribe(update, context):
    if not db.check_user(update.effective_user.id):
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=f"Сначала нужно нажать /start"
        )
        return
    if context.args:
        sub_tickers = list()
        for ticker in context.args:
            if db.check_ticker(ticker, update.effective_user.id):
                db.delete_subscribed_ticker(
                    ticker,
                    update.effective_user.name,
                    update.effective_user.id
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
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Не указаны тикеры, запустите команду так: /del_subscribe <TIK> или так /subscribe <TIK> <TIK> <TIK>",
        )
        return


@telegram.deploy(handler=CommandHandler)
def subscribe_pf(update, context):
    if not db.check_user(update.effective_user.id):
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
        tinkoff.subscribe_portfolio(
            tinkoff.get_portfolio(update.effective_user.id),
            update.effective_user.name,
            update.effective_user.id
        )
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=f"Подписка на портфель оформлена"
        )
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Эта функция, к сожалению не доступна для вас.",
        )


@telegram.deploy(handler=CommandHandler)
def unsubscribe_pf(update, context):
    if not db.check_user(update.effective_user.id):
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
        tinkoff.delete_subscribe_portfolio(
            tinkoff.get_portfolio(update.effective_user.id),
            update.effective_user.name,
            update.effective_user.id
        )
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=f"Подписка на портфель отключена"
        )
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Эта функция, к сожалению не доступна для вас.",
        )


@telegram.deploy(handler=CommandHandler)
def show_subscribe(update, context):
    if not db.check_user(update.effective_user.id):
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
    subscribe_list = db.show_list_of_subscribes(update.effective_user.name, update.effective_user.id)
    if subscribe_list:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            parse_mode="Markdown",
            text=f"`{tabulate(subscribe_list, headers=header, tablefmt='pipe', stralign='left')}`",
        )
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Ваш список на подписку пуст. Добавьте что-нибудь при помощи /subscribe",
        )


@telegram.deploy(handler=CommandHandler)
def show_ticker(update, context):
    if not db.check_user(update.effective_user.id):
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=f"Сначала нужно нажать /start"
        )
        return
    if context.args:
        for ticker in context.args:
            try:
                rez = tinkoff.show_brief_ticker_info_by_id(ticker, update.effective_user.id)
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
{rez['link']}"""
            context.bot.send_message(
                chat_id=update.effective_chat.id, parse_mode="Markdown", text=message
            )
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Не указаны тикеры, запустите команду так: /show_ticker <TIK> или так /show_ticker <TIK> <TIK> <TIK>",
        )


@telegram.deploy(handler=MessageHandler)
def unknown(update, context):
    logger.info(
        f"{update.effective_user.name} ({update.effective_user.id}) sent unknown command: {update.message.text}"
    )
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Такой команды нет, выбери нужную команду из списка.",
    )


@telegram.deploy(handler=MessageHandler)
def unknown_text(update, context):
    logger.info(
        f"{update.effective_user.name} ({update.effective_user.id}) sent unknown command: {update.message.text}"
    )
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Допускаются только команды /.",
    )


async def main():
    await asyncio.gather(interval_polling(), interval_news())


def run ():
    telegram.updater.start_polling()
    asyncio.new_event_loop().run_until_complete(main())


if __name__ == "__main__":
    run()

