import asyncio
import html
import json
import traceback
import yaml
import backoff
from dotenv import load_dotenv


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

unknown_command_handler = MessageHandler(
    Filters.command, unknown
)  # Если приходит команда, которую не знаем - пускаем функцию unknown
dispatcher.add_handler(unknown_command_handler)

unknown_text_handler = MessageHandler(
    Filters.text, unknown_text
)  # Отвечаем на любые не команды
dispatcher.add_handler(unknown_text_handler)


async def main():
    await asyncio.gather(interval_polling(), interval_news())


@backoff.on_exception(backoff.expo, Exception, max_tries=3)
def run ():
    updater.start_polling()
    asyncio.new_event_loop().run_until_complete(main())

if __name__ == "__main__":
    run()
