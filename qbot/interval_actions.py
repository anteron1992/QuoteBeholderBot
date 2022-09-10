from math import fabs
from qbot.logger import logger
from qbot.helpers import get_news_by_ticker


class Interval_actions:
    def __init__(self, app):
        self.config = app.config
        self.tinkoff = app.market['tinkoff']
        self.db = app.db

    async def ticker_polling(self, bot) -> bool:
        ticker_list = await self.tinkoff.get_username_tickers()
        for uid, result in ticker_list.items():
            for ticker in result:
                ticker_info = await self.tinkoff.show_brief_ticker_info_by_id(ticker, uid)
                if ticker_info:
                    if not isinstance(ticker_info["diff"], str):
                        if fabs(ticker_info["diff"]) >= self.config['reaction_percent']:
                            tik = ticker_info["ticker"]
                            message = f"<a href='https://bcs-express.ru/kotirovki-i-grafiki/{tik}'>{tik}</a> {ticker_info['diff']}%"
                            if ticker_info["diff"] > 0:
                                message = f"<a href='https://bcs-express.ru/kotirovki-i-grafiki/{tik}'>{tik}</a> +{ticker_info['diff']}%"
                            await bot.send_message(uid, message, parse_mode="HTML")
                            logger.info(
                                f"Ticker {ticker_info['ticker']} price is changed by {ticker_info['diff']}% message sent to {id}"
                            )
                            await self.db.override_price(ticker_info, uid)
                else:
                    logger.error(f"Тикер {ticker} c id {uid} не найден")

    async def news_polling(self, bot):
        special_tickers_dict = self.config['exceptions']
        ticker_list = await self.tinkoff.get_username_tickers()
        for uid, result in ticker_list.items():
            for ticker in result:
                rez = get_news_by_ticker(ticker, special_tickers_dict)
                if rez:
                    last = await self.db.get_time_of_last_news(ticker)
                    if last == "new" or last != rez["time"]:
                        message = (
                            f"<a href='{rez['href']}'>{ticker}</a>\n"
                            f"<em>{rez['time']}</em>\n"
                            f"<b>{rez['header']}</b>\n"
                            f"{rez['text']}\n"
                        )
                        await bot.send_message(uid, message, parse_mode="HTML")
                        logger.info(
                            f"Ticker {ticker} fresh news from {rez['time']} message sent to {uid}"
                        )
                        await self.db.update_news_info(ticker, rez, last)



