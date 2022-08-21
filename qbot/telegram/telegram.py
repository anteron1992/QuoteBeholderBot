from telegram import Bot, InlineQueryResultArticle, InputTextMessageContent, ParseMode
from os import getenv
from telegram.ext import (
    CommandHandler,
    Filters,
    InlineQueryHandler,
    MessageHandler,
    Updater,
)
from telegram.ext.dispatcher import run_async
from qbot.market.tinvest import Tinvest


class Telegram():
    """
    Class for representation of Telegram classes
    """
    def __init__(self):
        self.tinkoff = Tinvest()
        self.updater = Updater(token=getenv("TELE_TOKEN"))
        self.dispatcher = self.updater.dispatcher

    def start(self, update, context):
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="QuoteBeholder это бот, который информирует об резких изменениях котировок.\nУкажите команду после '/'",
        )
        self.tinkoff.db.add_new_user_to_db(update)