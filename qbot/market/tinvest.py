from os import getenv
from qbot.market.tinvest_api import TinvestAPI
from qbot.exceptions import TokenNotFound, AccountNotFound
from qbot.logger import logger


class Tinvest:
    """
    Class for representation of Tinkoff Invest python client
    """
    def __init__(self, db):
        self.db = db
        token = getenv("TINKOFF_TOKEN")
        if token and isinstance(token, str):
            self.api = TinvestAPI(token)
        else:
            logger.error("Start failed cause token not found")
            raise TokenNotFound("Tinkoff token 'TINKOFF_TOKEN' is not found into env vars!")

    def get_portfolio(self, acc_id: str = None):
        if not acc_id:
            acc_id = getenv("TINKOFF_ACCOUNT_ID")
        if acc_id:
            return self.api.get_portfolio(account_id=acc_id)
        else:
            raise AccountNotFound("Tinkoff account 'TINKOFF_ACCOUNT_ID' not found into env vars!")

    def search_ticker(self, ticker: str) -> dict:
        instruments = self.api.get_market_by_ticker(ticker)["payload"]["instruments"]
        if instruments:
            return instruments[0]

    def _get_price_by_figi(self, figi):
        return self.api.get_market_orderbook(figi=figi, depth=3)["payload"]["lastPrice"]

    async def subscribe_ticker(self, ticker: str, uname: str, uid: int) -> bool:
        if await self.db.check_user(uid):
            ticker_info = self.search_ticker(ticker)
            if ticker_info:
                price = self._get_price_by_figi(ticker_info['figi'])
                if not await self.db.check_ticker(ticker_info['ticker'], uid):
                    await self.db.subscribe_on_new_ticker(uname, uid, ticker_info, price)
                    return True
            return False

    async def subscribe_portfolio(self, portfolio: dict, uname: str, uid: int) -> bool:
        if await self.db.check_user(uid):
            for pos in portfolio["payload"]["positions"]:
                await self.subscribe_ticker(pos["ticker"], uname, uid)
            logger.info(f"{uname} ({uid}) subscribed own portfolio")
            return True
        else:
            return False

    async def delete_subscribe_portfolio(self, portfolio: dict, uname: str, uid: int) -> bool:
        if await self.db.check_user(uid):
            for pos in portfolio["payload"]["positions"]:
                await self.db.delete_subscribed_ticker(pos["ticker"], uname, uid)
                logger.info(f"{uname} ({uid}) unsubscribed own portfolio")
            return True
        else:
            return False

    async def show_brief_ticker_info_by_id(self, ticker: str, uid: int) -> dict:
        ticker_info = self.search_ticker(ticker)
        if ticker_info:
            price = self._get_price_by_figi(ticker_info['figi'])
            return await self.db.get_ticker_info_by_id(ticker_info, uid, price)

    async def show_summary_ticker_info(self, ticker: str, uname: str, uid: int) -> dict:
        ticker_info = self.search_ticker(ticker)
        if ticker_info:
            price = self._get_price_by_figi(ticker_info['figi'])
            return await self.db.get_summary_tickers_by_id(ticker_info, uname, uid, price)
        else:
            raise ValueError(f"Тикер {ticker} не найден")

    async def get_username_tickers(self) -> dict:
        polling_list = dict()
        users_table = await self.db.show_usernames()
        for line in users_table:
            polling_list.update({line: await self.db.show_list_of_subscribes_by_id(line)})
        return polling_list
