import sqlite3
from os import path
from qbot.logger import logger
from qbot.helpers import count_percent, path_db, path_scheme, path_tests_db
from pathlib import Path


class Database:
    def __init__(self, tests=False):
        self.scheme: Path = path_scheme
        if tests and path.exists(path_tests_db):
            self.name: str = 'test_tickers.db'
            self.tests = True
        elif not tests and path.exists(path_db):
            self.name: str = 'tickers.db'
            self.tests = False
        elif not path.exists(path_db):
            logger.info('Creating DB file')
            logger.info('Creating schema in DB')
            with open(self.scheme) as f:
                schema = f.read()
                _db = sqlite3.connect(path_db)
                _db.executescript(schema)
                _db.close()

    def add_new_user_to_db(self, uname: str, uid: int) -> bool:
        _db = sqlite3.connect(path_tests_db) if self.tests else sqlite3.connect(path_db)
        row = (uid, uname)
        try:
            with _db:
                query = "INSERT INTO usernames VALUES (?, ?, datetime('now'))"
                if not self.check_user(uid=uid):
                    _db.execute(query, row)
                    if not "test" in self.name:
                        logger.info(
                            f"New user {uname} ({uid}) added to db"
                        )
                    return True
                else:
                    return False
        except sqlite3.IntegrityError:
            pass

    def delete_user_from_db(self, uname: str, uid: int) -> bool:
        _db = sqlite3.connect(path_tests_db) if self.tests else sqlite3.connect(path_db)
        row = (uid, uname)
        try:
            with _db:
                query = "DELETE FROM usernames WHERE id=? AND username=?"
                if self.check_user(uid=uid):
                    _db.execute(query, row)
                    if not "test" in self.name:
                        logger.info(
                            f"User {uname} ({uid}) has been removed from db"
                        )
                    return True
                else:
                    return False
        except sqlite3.IntegrityError:
            pass

    def check_user(self, uid: int) -> bool:
        _db = sqlite3.connect(path_tests_db) if self.tests else sqlite3.connect(path_db)
        row = (uid,)
        try:
            query = f"SELECT * FROM usernames WHERE id=?;"
            with _db:
                if bool(list(_db.execute(query, row))):
                    return True
                else:
                    return False
        except (sqlite3.IntegrityError, sqlite3.OperationalError):
            pass

    def check_ticker(self, ticker: str, uid: int) -> bool:
        _db = sqlite3.connect(path_tests_db) if self.tests else sqlite3.connect(path_db)
        row = (uid, ticker.upper())
        try:
            with _db:
                query = "SELECT ticker FROM tickers WHERE id=? AND ticker=?"
                return bool(list(_db.execute(query, row)))
        except sqlite3.IntegrityError:
            pass

    def subscribe_on_new_ticker(self, uname: str, uid: int, ticker_info: dict, price: float) -> bool:
        _db = sqlite3.connect(path_tests_db) if self.tests else sqlite3.connect(path_db)
        if ticker_info:
            ticker = ticker_info["ticker"]
            name = ticker_info["name"]
            row = (
                uid,
                uname,
                ticker,
                name,
                price,
            )
            try:
                if not self.check_ticker(ticker, uid) and self.check_user(uid):
                    with _db:
                        query = "INSERT INTO tickers VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'))"
                        _db.execute(query, row)
                        if not "test" in self.name:
                            logger.info(
                                f"{uname} ({uid}) subscribed on new ticker {ticker}"
                            )
                        return True
                else:
                    return False
            except sqlite3.IntegrityError:
                pass

    def delete_subscribed_ticker(self, ticker: str, uname: str, uid: int) -> bool:
        _db = sqlite3.connect(path_tests_db) if self.tests else sqlite3.connect(path_db)
        row = (uid, ticker.upper())
        try:
            if self.check_ticker(ticker, uid) and self.check_user(uid):
                with _db:
                    query = "DELETE FROM tickers WHERE id=? AND ticker=?;"
                    _db.execute(query, row)
                    if not "test" in self.name:
                        logger.info(
                            f"{uname} ({uid}) unsubscribed from ticker {ticker.upper()}"
                        )
                    return True
            else:
                return False
        except sqlite3.IntegrityError:
            pass

    def show_list_of_subscribes(self, uname: str, uid: int) -> list:
        _db = sqlite3.connect(path_tests_db) if self.tests else sqlite3.connect(path_db)
        row = (uid,)
        try:
            with _db:
                query = f"SELECT ticker, name FROM tickers WHERE id=?;"
                if not "test" in self.name:
                    logger.info(
                        f"{uname} ({uid}) invoking list of subscribers"
                    )
                return _db.execute(query, row).fetchall()
        except sqlite3.IntegrityError:
            pass

    def show_list_of_subscribes_by_id(self, uid: int) -> list:
        _db = sqlite3.connect(path_tests_db) if self.tests else sqlite3.connect(path_db)
        row = (uid,)
        try:
            with _db:
                query = f"SELECT ticker FROM tickers WHERE id=?"
                return _db.execute(query, row).fetchall()
        except sqlite3.IntegrityError:
            pass

    def show_usernames(self):
        _db = sqlite3.connect(path_tests_db) if self.tests else sqlite3.connect(path_db)
        try:
            with _db:
                query = "SELECT id FROM usernames;"
                return _db.execute(query).fetchall()
        except sqlite3.IntegrityError:
            pass

    def get_ticker_info_by_id(self, ticker_info: dict, uid: int, price: float) -> dict:
        _db = sqlite3.connect(path_tests_db) if self.tests else sqlite3.connect(path_db)
        row = (uid, ticker_info["ticker"].upper())
        query = "SELECT * FROM tickers WHERE id=? AND ticker=?;"
        if self.check_user(uid):
            try:
                with _db:
                    result = _db.execute(query, row).fetchall()[0]
                    return {
                        "ticker": result[2],
                        "last_price": result[4],
                        "curr_price": price,
                        "diff": float(count_percent(result[4], price)),
                    }
            except (sqlite3.IntegrityError, sqlite3.OperationalError, IndexError):
                pass

    def get_summary_tickers_by_id(self, ticker_info: dict, uname: str, uid: int, price: float) -> dict:
        _db = sqlite3.connect(path_tests_db) if self.tests else sqlite3.connect(path_db)
        row = (uid, ticker_info["ticker"].upper())
        query = "SELECT * FROM tickers WHERE id=? AND ticker=?;"
        if self.check_user(uid):
            try:
                with _db:
                    result = _db.execute(query, row).fetchall()[0]
                    if not "test" in self.name:
                        logger.info(
                            f"{uname} ({uid}) invoking ticker {ticker_info['ticker'].upper()} info def"
                        )
                    return {
                        "ticker": result[2],
                        "name": result[3],
                        "last_price": result[4],
                        "curr_price": price,
                        "diff": str(count_percent(result[4], price)) + "%",
                        "link": "https://bcs-express.ru/kotirovki-i-grafiki/" + ticker_info["ticker"],
                    }
            except (sqlite3.IntegrityError, sqlite3.OperationalError, IndexError):
                return {
                    "ticker": ticker_info["ticker"],
                    "name": ticker_info["name"],
                    "last_price": "Тикер не добавлен в подписки",
                    "curr_price": price,
                    "diff": "Тикер не добавлен в подписки",
                    "link": "https://bcs-express.ru/kotirovki-i-grafiki/"
                            + ticker_info["ticker"],
                }

    def get_price_by_ticker(self, ticker: str, uid: int) -> float:
        _db = sqlite3.connect(path_tests_db) if self.tests else sqlite3.connect(path_db)
        row = (ticker,)
        query = "SELECT price FROM tickers WHERE ticker=?"
        if self.check_user(uid) and self.check_ticker(ticker, uid):
            try:
                with _db:
                    return float(list(_db.execute(query, row))[0][0])
            except sqlite3.IntegrityError:
                pass

    def override_price(self, ticker_info: dict, uid: int) -> bool:
        _db = sqlite3.connect(path_tests_db) if self.tests else sqlite3.connect(path_db)
        row = (ticker_info["curr_price"], uid, ticker_info["ticker"])
        query = "UPDATE tickers SET price=?, updated=datetime('now') WHERE id=? AND ticker=?;"
        if self.check_user(uid):
            try:
                with _db:
                    _db.execute(query, row)
            except sqlite3.IntegrityError:
                pass
            return True

    def get_time_of_last_news(self, ticker: str) -> str:
        _db = sqlite3.connect(path_tests_db) if self.tests else sqlite3.connect(path_db)
        row = (ticker,)
        query = f"SELECT time FROM news WHERE ticker=?"
        try:
            with _db:
                rez = _db.execute(query, row).fetchall()
                if rez:
                    return rez[0][0]
                else:
                    return "new"
        except sqlite3.IntegrityError:
            pass

    def update_news_info(self, ticker: str, news: dict) -> bool:
        _db = sqlite3.connect(path_tests_db) if self.tests else sqlite3.connect(path_db)
        row_create = (ticker, news["header"], news["time"])
        row_update = (news["header"], news["time"], ticker)
        try:
            with _db:
                if self.get_time_of_last_news(ticker) == "new":
                    query = "INSERT INTO news VALUES (?, ?, ?, datetime('now'));"
                    _db.execute(query, row_create)
                else:
                    query = "UPDATE news SET header=?, time=?, updated=datetime('now') WHERE ticker=?;"
                    _db.execute(query, row_update)
                return True
        except sqlite3.IntegrityError:
            pass
