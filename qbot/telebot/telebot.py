from os import getenv
from telegram.ext import (
    Updater,
    CommandHandler,
    Filters,
    MessageHandler,
)

from telegram import Bot, ParseMode

from qbot.market.tinvest import Tinvest
from qbot.db.database import Database


class Telebot():
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


