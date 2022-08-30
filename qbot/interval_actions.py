import asyncio
from math import fabs
from qbot.market.tinvest import Tinvest
from qbot.db.database import Database
from qbot.logger import logger
from qbot.telebot.telebot import Telebot
from qbot.helpers import get_news_by_ticker
from qbot.config.config import CONFIG

tinkoff = Tinvest()
db = Database()
telegram = Telebot()


async def interval_polling():
    print(1)
    flag = True
    while True:
        tickers = await tinkoff.get_username_tickers()
        for uid in tickers:
            for ticker in tickers[uid]:
                try:
                    rez = await tinkoff.show_brief_ticker_info_by_id(ticker[0], uid)
                except Exception as err:
                    logger.error(f"Тикер {ticker[0]} c id {uid} не найден ({err})")
                    rez = None
                if rez and fabs(rez["diff"]) >= CONFIG['reaction_percent']:
                    flag = False
                    tik = rez["ticker"]
                    diff = rez["diff"]
                    message = f"<a href='https://bcs-express.ru/kotirovki-i-grafiki/{tik}'>{tik}</a> {diff}%"
                    if rez["diff"] > 0:
                        message = f"<a href='https://bcs-express.ru/kotirovki-i-grafiki/{tik}'>{tik}</a> +{diff}%"
                    telegram.send_message(uid, message)
                    logger.info(
                        f"Ticker {rez['ticker']} price is changed by {rez['diff']}% message sent to {id}"
                    )
                    await db.override_price(rez, uid)

        await asyncio.sleep(CONFIG['polling_interval'])


async def interval_news():
    print(2)
    special_tickers_dict = CONFIG['exceptions']
    while True:
        tickers = await tinkoff.get_username_tickers()
        for uid in tickers:
            for ticker in tickers[uid]:
                rez = get_news_by_ticker(ticker[0], special_tickers_dict)
                last = await db.get_time_of_last_news(ticker[0])
                if rez and last:
                    if last != rez["time"]:
                        message = (
                            f"<a href='{rez['href']}'>{ticker[0]}</a>\n"
                            f"<em>{rez['time']}</em>\n"
                            f"<b>{rez['header']}</b>\n"
                            f"{rez['text']}\n"
                        )
                        telegram.send_message(uid, message)
                        logger.info(
                            f"Ticker {ticker[0]} fresh news from {rez['time']} message sent to {uid}"
                        )
                        await db.update_news_info(ticker[0], rez)
        await asyncio.sleep(CONFIG['news_interval'])
