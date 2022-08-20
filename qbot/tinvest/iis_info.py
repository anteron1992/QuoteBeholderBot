from tinvestor import Tinvest
from auth import SAND_TOKEN
from pprint import pprint
from datetime import datetime

if __name__ =="__main__":
    client = Tinvest(SAND_TOKEN)
    #pprint (client.get_user_accounts())
    pprint (client.get_portfolio(account_id=2042625489))
    #pprint (client.get_market_stocks())
    #pprint (client.get_market_by_ticker("USD000UTSTOM"))
    #pprint (client.get_market_by_ticker("EUR_RUB__TOM"))
    #pprint(client.get_market_by_figi("BBG0047315Y7"))
    #pprint (client.get_operations(frm="2020-09-01T17:43:33+03:00",
    #                              to="2021-07-24T17:43:33+03:00",
    #                              ticker="CHMF",
    #                              account_id=2042625489))
    #pprint (client.get_portfolio_currencies(2039981838))
    #pprint (client.get_market_orderbook(ticker="USD000UTSTOM", depth=1))
    #pprint(client.get_market_orderbook(ticker="EUR_RUB__TOM", depth=1))
    pprint (datetime.today().strftime("%Y-%M-%dT%H:%M:00+03:00"))
