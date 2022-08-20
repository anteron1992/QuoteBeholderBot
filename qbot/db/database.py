# -*- coding: utf-8 -*-
import sqlite3
from os import path
from qbot.logger import logger


class Database:
    def __init__(self, name: str = 'tickers_tests.db'):
        self.name: str = name
        self.scheme: str = 'tickers_scheme.sql'
        self._exist: bool = path.exists(name)
        self._db = sqlite3.connect(self.name)

        if not self._exist:
            logger.info('Creating DB file')
            logger.info ('Creating schema in DB')
            with open (self.scheme) as f:
                schema = f.read()
                self._db.executescript(schema)
            self._db.close()
        else:
            logger.warning('DB file already created!')


    def check_ticker(self, ticker: str, uid: int) -> bool:
        row = (uid, ticker.upper())
        try:
            with self._db:
                query = "SELECT ticker FROM tickers WHERE id=? AND ticker=?"
                return bool(list(self._db.execute(query, row)))
        except sqlite3.IntegrityError:
            pass


    def add_new_user_to_db(self, uname: str, uid: int) -> None:
        row = (uid, uname)
        try:
            with self._db:
                query = "INSERT INTO usernames VALUES (?, ?, datetime('now'))"
                connect.execute(query, row)
                logger.info(
                    f"New user {uname} ({uid}) added to db"
                )
        except sqlite3.IntegrityError:
            pass



if __name__ == '__main__':
    db = Database()
    print (db.check_ticker("SBER", uid=176549646))
