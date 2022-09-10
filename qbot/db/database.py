import asyncpg
import qbot.exceptions as exceptions
from pathlib import Path
from typing import Iterable, Any
from qbot.config.config import CONFIG, path_scheme, test_scheme
from qbot.helpers import count_percent
from qbot.logger import logger


class DatabaseConnect:
    def __init__(self, host, port, database, user, password, tests=False):
        self.connect = None
        self.config = {
            "host": host,
            "port": port,
            "database": CONFIG['db_test'] if tests else database,
            "user": user,
            "password": password,
        }

    async def __aenter__(self):
        logger.info(f'Try to connect to database {self.config["database"]}')
        try:
            self.connection = await asyncpg.connect(**self.config)
            return self.connection
        except asyncpg.exceptions.ConnectionDoesNotExistError as err:
            logger.critical(
                f"Unable connect to {self.config['database']}: {err}"
            )
            raise exceptions.DatabaseConnectionError

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        logger.info(f'Closing connection to database {self.config["database"]}')
        await self.connection.close()


class Database:

    _pool = []

    def __init__(self, tests=False):
        self.scheme: Path = path_scheme if path_scheme.exists() else None
        self.test_scheme: Path = test_scheme if test_scheme.exists() else None
        self.tests = tests
        self.config = CONFIG['postgresql']

    async def init(self):
        logger.info('Database initialisation')
        # Use default template1 for prod db creation
        async with DatabaseConnect(
                host=self.config['host'],
                port="5432",
                database="template1",
                user="postgres",
                password=CONFIG['db_defpass']
        ) as conn:
            try:
                await conn.execute(f"CREATE DATABASE {self.config['database']};")
                await conn.execute(f"CREATE DATABASE {CONFIG['db_test']};")
            except asyncpg.exceptions.DuplicateDatabaseError:
                logger.info('Database qbot already exists')
            try:
                await conn.execute(
                    f"""
                    CREATE USER {self.config['user']} WITH PASSWORD '{self.config['password']}';
                    GRANT ALL PRIVILEGES ON DATABASE 
                    {self.config['database']}, {CONFIG['db_test']} TO {self.config['user']};
                    """
                )
            except asyncpg.exceptions.DuplicateObjectError:
                logger.info('Role qbot already exists')

        # Scheme database creation
        if self.scheme and self.test_scheme:
            with open(self.scheme) as f, open(self.test_scheme) as tf:
                schema = f.read()
                t_schema = tf.read()
                if self.tests:
                    self.config["database"] = CONFIG['db_test']
                async with DatabaseConnect(**self.config) as _db:
                    try:
                        await _db.execute(schema)
                    except asyncpg.exceptions.DuplicateTableError:
                        logger.warning("Database scheme initialised already, skip...")
                    if self.tests and not await _db.fetchrow("SELECT * FROM tickers;"):
                        await _db.execute(t_schema)
        else:
            logger.critical("SQL Scheme not found!")
            raise exceptions.DatabaseSchemeError
        self._pool.append(await asyncpg.create_pool(**self.config, max_size=100))
        logger.info(f'Database initialisation completed')

    async def close_pool(self):
        await self._pool[0].release(self._pool)

    async def add_new_user_to_db(self, uname: str, uid: int) -> bool:
        query = [
            """
        INSERT INTO usernames VALUES ($1, $2, to_char(now(), 'YYYY-MM-DD HH24:MI:SS'));
        """, uid, uname
        ]
        async with self._pool[0].acquire() as _db:
            if not await self.check_user(uid=uid):
                add = bool(await _db.execute(*query))
                logger.info(f"New user with ID {uid} has been added to db")
                return add
            return False

    async def delete_user_from_db(self, uname: str, uid: int) -> bool:
        query = [
            """
        DELETE FROM usernames WHERE id=$1 AND username=$2;
        """, uid, uname
        ]
        async with self._pool[0].acquire() as _db:
            if await self.check_user(uid=uid):
                return bool(await _db.execute(*query))
            return False

    async def check_user(self, uid: int) -> bool:
        query = ["SELECT 1 FROM usernames WHERE id=$1;", uid]
        async with self._pool[0].acquire() as _db:
            return bool(await _db.fetchrow(*query))

    async def check_ticker(self, ticker: str, uid: int) -> bool:
        query = ["SELECT ticker FROM tickers WHERE id=$1 AND ticker=$2;", uid, ticker.upper()]
        async with self._pool[0].acquire() as _db:
            return bool(await _db.fetchrow(*query))

    async def subscribe_on_new_ticker(self, uname: str, uid: int, ticker_info: dict, price: float) -> bool:
        if ticker_info and not await self.check_ticker(ticker_info["ticker"], uid):
            ticker = ticker_info["ticker"]
            name = ticker_info["name"]
            row = [
                uid,
                uname,
                ticker,
                name,
                price,
            ]
            query = [
                """
            INSERT INTO tickers VALUES (
            $1, $2, $3, $4, $5, 
            to_char(now(), 'YYYY-MM-DD HH24:MI:SS'), 
            to_char(now(), 'YYYY-MM-DD HH24:MI:SS')
            );
            """, *row
            ]
            async with self._pool[0].acquire() as _db:
                result = await _db.execute(*query)
                logger.info(f"{uname} ({uid}) subscribed on new ticker {ticker}")
                return bool(result)
        return False

    async def delete_subscribed_ticker(self, ticker: str, uname: str, uid: int) -> bool:
        query = ["DELETE FROM tickers WHERE id=$1 AND ticker=$2;", uid, ticker.upper()]
        if await self.check_ticker(ticker, uid) and await self.check_user(uid):
            async with self._pool[0].acquire() as _db:
                result = await _db.execute(*query)
                logger.info(f"{uname} ({uid}) unsubscribed from ticker {ticker.upper()}")
                return bool(result)
        return False

    async def show_list_of_subscribes(self, uname: str, uid: int) -> Iterable[Any]:
        query = ["SELECT ticker, name FROM tickers WHERE id=$1;", uid]
        async with self._pool[0].acquire() as _db:
            result = await _db.fetch(*query)
            logger.info(f"{uname} ({uid}) invoking list of subscribers")
            result = [(k, v) for k, v in dict(result).items()]
            return result

    async def show_list_of_subscribes_by_id(self, uid: int) -> Iterable[Any]:
        query = [f"SELECT ticker FROM tickers WHERE id=$1", uid]
        ticker_list = []
        async with self._pool[0].acquire() as _db:
            result = await _db.fetch(*query)
            for ticker in tuple(result):
                ticker_list += list(ticker)
            return ticker_list

    async def show_usernames(self) -> Iterable[Any]:
        query = ["SELECT id FROM usernames;"]
        user_list = []
        async with self._pool[0].acquire() as _db:
            result = await _db.fetch(*query)
            for user in tuple(result):
                user_list += list(user)
            return user_list

    async def get_ticker_info_by_id(self, ticker_info: dict, uid: int, price: float) -> dict:
        query = ["SELECT * FROM tickers WHERE id=$1 AND ticker=$2;", uid, ticker_info["ticker"].upper()]
        if await self.check_user(uid):
            async with self._pool[0].acquire() as _db:
                result = await _db.fetchrow(*query)
                if result:
                    result = dict(result)
                    return {
                       "name": result["name"],
                       "ticker": result["ticker"],
                       "last_price":  result["price"],
                       "curr_price": price,
                       "diff": float(count_percent(result["price"], price)),
                    }
                else:
                    return {
                            "name": ticker_info['name'],
                            "ticker": ticker_info['ticker'],
                            "last_price": "Тикер не добавлен в подписки",
                            "curr_price": price,
                            "diff": "Тикер не добавлен в подписки"
                        }

    async def get_summary_tickers_by_id(self, ticker_info: dict, uname: str, uid: int, price: float) -> dict:
        query = ["SELECT * FROM tickers WHERE id=$1 AND ticker=$2;", uid, ticker_info["ticker"].upper()]
        if await self.check_user(uid):
            async with self._pool[0].acquire() as _db:
                result = await _db.fetchrow(*query)
                logger.info(f"{uname} ({uid}) invoking ticker {ticker_info['ticker'].upper()} info def")
                if result:
                    result = dict(result)
                    return {
                        "name": result["name"],
                        "ticker": result["ticker"],
                        "last_price": result["price"],
                        "curr_price": price,
                        "diff": str(count_percent(result["price"], price)) + "%",
                        "link": "https://bcs-express.ru/kotirovki-i-grafiki/" + result["ticker"],
                    }
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
        query = ["SELECT price FROM tickers WHERE ticker=$1;", ticker]
        if await self.check_user(uid) and await self.check_ticker(ticker, uid):
            async with self._pool[0].acquire() as _db:
                result = await _db.fetchrow(*query)
                return tuple(result)[0]

    async def override_price(self, ticker_info: dict, uid: int) -> bool:
        query = [
            """
            UPDATE tickers SET price=$1, updated=to_char(now(), 'YYYY-MM-DD HH24:MI:SS') 
            WHERE id=$2 AND ticker=$3;
            """, ticker_info["curr_price"], uid, ticker_info["ticker"]
        ]
        if await self.check_user(uid) and await self.check_ticker(ticker_info["ticker"], uid):
            async with self._pool[0].acquire() as _db:
                return bool(await _db.execute(*query))
        return False

    async def get_time_of_last_news(self, ticker: str) -> str:
        query = [f"SELECT time FROM news WHERE ticker=$1", ticker]
        async with self._pool[0].acquire() as _db:
            result = await _db.fetchrow(*query)
            if result:
                return tuple(result)[0]
            else:
                return "new"

    async def update_news_info(self, ticker: str, news: dict, last: str) -> bool:
        row_create = [ticker, news["header"], news["time"]]
        row_update = [news["header"], news["time"], ticker]
        async with self._pool[0].acquire() as _db:
            if last == "new":
                query = [
                    """
                    INSERT INTO news VALUES ($1, $2, $3, to_char(now(), 'YYYY-MM-DD HH24:MI:SS'));
                    """, *row_create
                ]
                return bool(await _db.execute(*query))
            else:
                query = [
                    """
                    UPDATE news SET header=$1, time=$2, 
                    updated=to_char(now(), 'YYYY-MM-DD HH24:MI:SS') WHERE ticker=$3;
                    """, *row_update
                ]
                return bool(await _db.execute(*query))

    async def delete_news_from_db(self, ticker: str) -> bool:
        query = [f"DELETE FROM news WHERE ticker=$1;", ticker]
        async with self._pool[0].acquire() as _db:
            return bool(await _db.execute(*query))
