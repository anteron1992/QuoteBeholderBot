# -*- coding: utf-8 -*-
import sqlite3
from os import path

DB_NAME = 'tickers.db'
DB_EXIST = path.exists(DB_NAME)
DB_SCHEMA = 'tickers_scheme.sql'

def conndb ():
    '''
    Создаём файл базы данных если файл еще не создан
    в противном случае вернёт ошибку.
    '''
    if not DB_EXIST:
        print ('Creating DB file...')
        connect = sqlite3.connect(DB_NAME)
        print ('Creating schema in DB...')
        with open (DB_SCHEMA) as f:
            schema = f.read()
            connect.executescript(schema)
        connect.close()
    else:
        print ('WARNING:  DB file already created!')


if __name__ == '__main__':
    conndb()
