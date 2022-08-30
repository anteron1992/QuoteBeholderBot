import sqlite3
import asyncio
import aiosqlite
from pathlib import Path
from typing import Iterable,Any
from qbot.config import config
from qbot.helpers import count_percent
from qbot.logger import logger


class Database:
    def __init__(self, tests=False):
        self.scheme: Path = config.path_scheme
        if tests and Path.exists(config.path_tests_db):
            self.name: str = 'test_tickers.db'
            self._db = config.path_tests_db
        elif not tests and Path.exists(config.path_db):
            self.name: str = 'tickers.db'
            self._db = config.path_db
        elif not Path.exists(config.path_db):
            logger.info('Creating DB file')
            logger.info('Creating schema in DB')
            with open(self.scheme) as f:
                schema = f.read()
                _db = sqlite3.connect(config.path_db)
                _db.executescript(schema)
                _db.close()

    async def add_new_user_to_db(self, uname: str, uid: int) -> bool:
        row = (uid, uname)
        query = "INSERT INTO usernames VALUES (?, ?, datetime('now'))"
        try:
            async with aiosqlite.connect(self._db) as _db:
                if not await self.check_user(uid=uid):
                    await _db.execute(query, row)
                    await _db.commit()
                    if not "test" in self.name:
                        logger.info(
                            f"New user {uname} ({uid}) added to db"
                        )
                    return True
                else:
                    return False
        except sqlite3.IntegrityError:
            pass

    async def delete_user_from_db(self, uname: str, uid: int) -> bool:
        row = (uid, uname)
        query = "DELETE FROM usernames WHERE id=? AND username=?"
        try:
            async with aiosqlite.connect(self._db) as _db:
                if await self.check_user(uid=uid):
                    await _db.execute(query, row)
                    await _db.commit()
                    if not "test" in self.name:
                        logger.info(
                            f"User {uname} ({uid}) has been removed from db"
                        )
                    return True
                else:
                    return False
        except sqlite3.IntegrityError:
            pass

    async def check_user(self, uid: int) -> bool:
        row = (uid,)
        query = f"SELECT * FROM usernames WHERE id=?;"
        try:
            async with aiosqlite.connect(self._db) as _db:
                cursor = await _db.execute(query, row)
                if await cursor.fetchall():
                    return True
                else:
                    return False
        except (sqlite3.IntegrityError, sqlite3.OperationalError):
            pass

    async def check_ticker(self, ticker: str, uid: int) -> bool:
        row = (uid, ticker.upper())
        query = "SELECT ticker FROM tickers WHERE id=? AND ticker=?"
        try:
            async with aiosqlite.connect(self._db) as _db:
                cursor = await _db.execute(query, row)
                return bool(await cursor.fetchall())
        except sqlite3.IntegrityError:
            pass

    async def subscribe_on_new_ticker(self, uname: str, uid: int, ticker_info: dict, price: float) -> bool:
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
                if not await self.check_ticker(ticker, uid) and await self.check_user(uid):
                    async with aiosqlite.connect(self._db) as _db:
                        query = "INSERT INTO tickers VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'))"
                        await _db.execute(query, row)
                        await _db.commit()
                        if not "test" in self.name:
                            logger.info(
                                f"{uname} ({uid}) subscribed on new ticker {ticker}"
                            )
                        return True
                else:
                    return False
            except sqlite3.IntegrityError:
                pass

    async def delete_subscribed_ticker(self, ticker: str, uname: str, uid: int) -> bool:
        row = (uid, ticker.upper())
        query = "DELETE FROM tickers WHERE id=? AND ticker=?;"
        try:
            if await self.check_ticker(ticker, uid) and await self.check_user(uid):
                async with aiosqlite.connect(self._db) as _db:
                    await _db.execute(query, row)
                    await _db.commit()
                    if not "test" in self.name:
                        logger.info(
                            f"{uname} ({uid}) unsubscribed from ticker {ticker.upper()}"
                        )
                    return True
            else:
                return False
        except sqlite3.IntegrityError:
            pass

    async def show_list_of_subscribes(self, uname: str, uid: int) -> Iterable[Any]:
        row = (uid,)
        query = "SELECT ticker, name FROM tickers WHERE id=?;"
        try:
            async with aiosqlite.connect(self._db) as _db:
                if not "test" in self.name:
                    logger.info(
                        f"{uname} ({uid}) invoking list of subscribers"
                    )
                cursor = await _db.execute(query, row)
                return await cursor.fetchall()
        except sqlite3.IntegrityError:
            pass

    async def show_list_of_subscribes_by_id(self, uid: int) -> Iterable[Any]:
        row = (uid,)
        query = f"SELECT ticker FROM tickers WHERE id=?"
        try:
            async with aiosqlite.connect(self._db) as _db:
                cursor = await _db.execute(query, row)
                return await cursor.fetchall()
        except sqlite3.IntegrityError:
            pass

    async def show_usernames(self) -> Iterable[Any]:
        query = "SELECT id FROM usernames;"
        try:
            async with aiosqlite.connect(self._db) as _db:
                cursor = await _db.execute(query)
                return await cursor.fetchall()
        except sqlite3.IntegrityError:
            pass

    async def get_ticker_info_by_id(self, ticker_info: dict, uid: int, price: float) -> dict:
        row = (uid, ticker_info["ticker"].upper())
        query = "SELECT * FROM tickers WHERE id=? AND ticker=?;"
        if await self.check_user(uid):
            try:
                async with aiosqlite.connect(self._db) as _db:
                    cursor = await _db.execute(query, row)
                    result = await cursor.fetchall()
                    return {
                       "name": result[0][3],
                       "ticker": result[0][2],
                       "last_price": result[0][4],
                       "curr_price": price,
                       "diff": float(count_percent(result[0][4], price)),
                    }
            except (sqlite3.IntegrityError, sqlite3.OperationalError, IndexError):
                pass

    async def get_summary_tickers_by_id(self, ticker_info: dict, uname: str, uid: int, price: float) -> dict:
        row = (uid, ticker_info["ticker"].upper())
        query = "SELECT * FROM tickers WHERE id=? AND ticker=?;"
        if await self.check_user(uid):
            try:
                async with aiosqlite.connect(self._db) as _db:
                    cursor = await _db.execute(query, row)
                    result = await cursor.fetchall()
                    if not "test" in self.name:
                        logger.info(
                            f"{uname} ({uid}) invoking ticker {ticker_info['ticker'].upper()} info def"
                        )
                    return {
                        "ticker": result[0][2],
                        "name": result[0][3],
                        "last_price": result[0][4],
                        "curr_price": price,
                        "diff": str(count_percent(result[0][4], price)) + "%",
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

    async def get_price_by_ticker(self, ticker: str, uid: int) -> float:
        row = (ticker,)
        query = "SELECT price FROM tickers WHERE ticker=?"
        if await self.check_user(uid) and await self.check_ticker(ticker, uid):
            try:
                async with aiosqlite.connect(self._db) as _db:
                    cursor = await _db.execute(query, row)
                    result = await cursor.fetchall()
                    return float(result[0][0])
            except sqlite3.IntegrityError:
                pass

    async def override_price(self, ticker_info: dict, uid: int) -> bool:
        row = (ticker_info["curr_price"], uid, ticker_info["ticker"])
        query = "UPDATE tickers SET price=?, updated=datetime('now') WHERE id=? AND ticker=?;"
        if await self.check_user(uid):
            try:
                async with aiosqlite.connect(self._db) as _db:
                    await _db.execute(query, row)
                    await _db.commit()
            except sqlite3.IntegrityError:
                pass
            return True

    async def get_time_of_last_news(self, ticker: str) -> str:
        row = (ticker,)
        query = f"SELECT time FROM news WHERE ticker=?"
        try:
            async with aiosqlite.connect(self._db) as _db:
                cursor = await _db.execute(query, row)
                result = await cursor.fetchall()
                if result:
                    return result[0][0]
                else:
                    return "new"
        except sqlite3.IntegrityError:
            pass

    async def update_news_info(self, ticker: str, news: dict) -> bool:
        row_create = (ticker, news["header"], news["time"])
        row_update = (news["header"], news["time"], ticker)
        try:
            async with aiosqlite.connect(self._db) as _db:
                if await self.get_time_of_last_news(ticker) == "new":
                    query = "INSERT INTO news VALUES (?, ?, ?, datetime('now'));"
                    await _db.execute(query, row_create)
                    await _db.commit()
                else:
                    query = "UPDATE news SET header=?, time=?, updated=datetime('now') WHERE ticker=?;"
                    await _db.execute(query, row_update)
                    await _db.commit()
                return True
        except sqlite3.IntegrityError:
            pass


# async def main():
#    a = Database(tests=True)
#    print(await a.add_new_user_to_db("Test", uid=123456789))
    # print(await a.check_user(uid=123456789) == True)
    # print(await a.delete_user_from_db("Test", uid=123456789))
    # print(await a.check_user(uid=176549646))
    # print(await a.check_ticker("AAPL", uid=176549646))
    # print(await a.get_price_by_ticker("AAPL", uid=176549646))


#asyncio.run(main())
