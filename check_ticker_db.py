from sys import argv
import create_db
import sqlite3

def check_ticker_in_db (ticker):
    connect = sqlite3.connect(create_db.DB_NAME)
    try:
        with connect:
            query = f"SELECT ticker FROM tickers WHERE ticker='{ticker}'"
            if [line for line in connect.execute(query)]:
                return True
            else:
                return False
    except sqlite3.IntegrityError:
        pass

if __name__ == '__main__':
    print (check_ticker_in_db(argv[1]))
