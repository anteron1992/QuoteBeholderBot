from os import getenv
from dotenv import load_dotenv
from tinvest_api import TinvestAPI
from qbot.exceptions import TokenNotFound
from qbot.logger import logger


class Tinvest:
    """
    Class for represetation of Tinkoff Invest python client
    """
    def __init__(self, token=None):
        TOKEN_NAME = "SAND_TOKEN"
        if not token:
            load_dotenv("../../auth.env")
            token = getenv(TOKEN_NAME)
        if token and isinstance(token,str):
            self.client = TinvestAPI(token)
        else:
            logger.error("Start failed cause token not found")
            raise TokenNotFound (f"{TOKEN_NAME} is not found into env vars")

    def search_ticker(self, ticker: str) -> dict:
        return self.client.get_market_by_ticker(ticker)


def test():
    from rich.pretty import pprint
    a = Tinvest()
    pprint(a.search_ticker("AAPL"))

if __name__ == "__main__":
    test()


