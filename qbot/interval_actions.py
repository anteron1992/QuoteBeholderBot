from math import fabs
from qbot.logger import logger
from qbot.helpers import get_news_by_ticker


class Interval_actions:
    def __init__(self, app):
        self.config = app.config
        self.tinkoff = app.market['tinkoff']
        self.db = app.db

    async def ticker_polling(self, bot):
        tickers = await self.tinkoff.get_username_tickers()
        for uid in tickers:
            for ticker in tickers[uid]:
                try:
                    rez = await self.tinkoff.show_brief_ticker_info_by_id(ticker[0], uid)
                except Exception as err:
                    logger.error(f"Тикер {ticker[0]} c id {uid} не найден ({err})")
                    rez = None
                if rez and fabs(rez["diff"]) >= self.config['reaction_percent']:
                    tik = rez["ticker"]
                    diff = rez["diff"]
                    message = f"<a href='https://bcs-express.ru/kotirovki-i-grafiki/{tik}'>{tik}</a> {diff}%"
                    if rez["diff"] > 0:
                        message = f"<a href='https://bcs-express.ru/kotirovki-i-grafiki/{tik}'>{tik}</a> +{diff}%"
                    await bot.send_message(uid, message, parse_mode="HTML")
                    logger.info(
                        f"Ticker {rez['ticker']} price is changed by {rez['diff']}% message sent to {id}"
                    )
                    await self.db.override_price(rez, uid)

    async def news_polling(self, bot):
        special_tickers_dict = self.config['exceptions']
        tickers = await self.tinkoff.get_username_tickers()
        for uid in tickers:
            for ticker in tickers[uid]:
                rez = get_news_by_ticker(ticker[0], special_tickers_dict)
                if rez:
                    logger.info(
                        f"[{uid}] Has got new news by ticker {ticker[0]}, checking..."
                    )
                last = await self.db.get_time_of_last_news(ticker[0])
                if rez and last:
                    if last == "new":
                        logger.info(
                            f"[{uid}] There is no any news {ticker[0]}, add to db..."
                        )
                    if last != rez["time"]:
                        message = (
                            f"<a href='{rez['href']}'>{ticker[0]}</a>\n"
                            f"<em>{rez['time']}</em>\n"
                            f"<b>{rez['header']}</b>\n"
                            f"{rez['text']}\n"
                        )
                        await bot.send_message(uid, message, parse_mode="HTML")
                        logger.info(
                            f"Ticker {ticker[0]} fresh news from {rez['time']} message sent to {uid}"
                        )
                        await self.db.update_news_info(ticker[0], rez, last)
