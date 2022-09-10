from qbot.db.database import Database
from qbot.market.tinvest import Tinvest
from qbot.config.config import CONFIG


class __Init_app:
    def __init__(self, tests):
        self.config = CONFIG
        self.db = Database(tests)
        self.market = {
            "tinkoff": Tinvest(self.db)
        }


def application(tests=False):
    obj = __Init_app(tests)
    return obj
