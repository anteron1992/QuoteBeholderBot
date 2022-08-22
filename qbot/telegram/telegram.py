from qbot import logger
from os import getenv
from telegram.ext import (
    Updater,
    CommandHandler,
    Filters,
    MessageHandler,
)

from telegram import Bot, ParseMode

from tabulate import tabulate
from qbot.market.tinvest import Tinvest
from qbot.db.database import Database
from qbot.logger import logger


class Telegram():
    """
    Class for representation of Telegram classes
    """
    def __init__(self):
        self.tinkoff = Tinvest()
        self.db = Database()
        self.updater = Updater(token=getenv("TELE_TOKEN"))
        self.dispatcher = self.updater.dispatcher

    @staticmethod
    def send_message(uid, message, parse_mode=ParseMode.HTML):
        sender = Bot(token=getenv("TELE_TOKEN"))
        sender.sendMessage(
            chat_id=uid, parse_mode=parse_mode, text=message
        )

    def deploy (self, handler):
        def wrapper (func):
            if handler == CommandHandler:
                start_handler = handler(func.__name__, func)
                self.dispatcher.add_handler(start_handler)
            elif handler == MessageHandler and func.__name__ == 'unknown_text':
                unknown_text_handler = MessageHandler(Filters.text, func)  # Default handler for unknown text
                self.dispatcher.add_handler(unknown_text_handler)
            elif handler == MessageHandler and func.__name__ == 'unknown':
                unknown_command_handler = handler(Filters.command, func)
                self.dispatcher.add_handler(unknown_command_handler)  # Default handler for unknown commands
        return wrapper

    @deploy(handler=CommandHandler)
    def start(self, update, context):
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="QuoteBeholder это бот, который информирует об резких изменениях котировок.\nУкажите команду после '/'",
        )
        self.db.add_new_user_to_db(update.effective_user.id, update.effective_user.name)

    @deploy(handler=CommandHandler)
    def subscribe(self, update, context):
        if not self.db.check_user(update.effective_user.id):
            context.bot.send_message(
                chat_id=update.effective_chat.id, text=f"Сначала нужно нажать /start"
            )
            return
        if context.args:
            sub_tickers = list()
            for ticker in context.args:
                if not self.db.check_ticker(ticker, update.effective_user.id):
                    try:
                        self.tinkoff.subscribe_ticker(ticker,
                            update.effective_user.name,
                            update.effective_user.id)
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

    @deploy(handler=CommandHandler)
    def unsubscribe(self, update, context):
        if not self.db.check_user(update.effective_user.id):
            context.bot.send_message(
                chat_id=update.effective_chat.id, text=f"Сначала нужно нажать /start"
            )
            return
        if context.args:
            sub_tickers = list()
            for ticker in context.args:
                if self.db.check_ticker(ticker, update.effective_user.id):
                    self.db.delete_subscribed_ticker(
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

    @deploy(handler=CommandHandler)
    def subscribe_pf(self, update, context):
        if not self.db.check_user(update.effective_user.id):
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
            self.tinkoff.subscribe_portfolio(
                self.tinkoff.get_portfolio(update.effective_user.id),
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

    @deploy(handler=CommandHandler)
    def unsubscribe_pf(self, update, context):
        if not self.db.check_user(update.effective_user.id):
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
            self.tinkoff.delete_subscribe_portfolio(
                self.tinkoff.get_portfolio(update.effective_user.id),
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

    @deploy(handler=CommandHandler)
    def show_subscribe(self, update, context):
        if not self.db.check_user(update.effective_user.id):
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
        subscribe_list = self.db.show_list_of_subscribes(update.effective_user.name, update.effective_user.id)
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

    @deploy(handler=CommandHandler)
    def show_ticker(self, update, context):
        if not self.db.check_user(update.effective_user.id):
            context.bot.send_message(
                chat_id=update.effective_chat.id, text=f"Сначала нужно нажать /start"
            )
            return
        if context.args:
            for ticker in context.args:
                try:
                    rez = self.tinkoff.show_brief_ticker_info_by_id(ticker, update.effective_user.id)
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

    @deploy(handler=MessageHandler)
    def unknown(self, update, context):
        logger.info(
            f"{update.effective_user.name} ({update.effective_user.id}) sent unknown command: {update.message.text}"
        )
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Такой команды нет, выбери нужную команду из списка.",
        )

    @deploy(handler=MessageHandler)
    def unknown_text(self, update, context):
        logger.info(
            f"{update.effective_user.name} ({update.effective_user.id}) sent unknown command: {update.message.text}"
        )
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Допускаются только команды /.",
        )