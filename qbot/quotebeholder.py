import asyncio
from qbot.logger import logger
from qbot.app.application import application
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from qbot.telebot.telebot import dp, bot
from qbot.interval_actions import Interval_actions

app = application()
actions = Interval_actions(app)


async def main():
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(actions.ticker_polling, "interval", minutes=app.config['ticker_interval'])
    scheduler.add_job(actions.news_polling, "interval", minutes=app.config['news_interval'])
    scheduler.start()
    try:
        await dp.start_polling()
    finally:
        bot.get_session().close()
        scheduler.shutdown()
        await asyncio.sleep(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit, RuntimeError):
        print("Bot stopped!")
