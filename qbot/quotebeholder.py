import asyncio
from qbot.telegram.telegram import Telegram
from qbot.interval_actions import interval_polling, interval_news

telegram = Telegram()


async def main():
    await asyncio.gather(interval_polling(), interval_news())

def run ():
    telegram.updater.start_polling()
    asyncio.new_event_loop().run_until_complete(main())

if __name__ == "__main__":
    run()

