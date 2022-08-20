from tinvestor import Tinvest
from auth import SAND_TOKEN
from pprint import pprint
from tabulate import tabulate
from datetime import datetime, timedelta, time

client = Tinvest(SAND_TOKEN)
portfolio = client.get_portfolio(account_id=2042625489)['payload']['positions']

def colorize(value, cont):
    if float(value) > 0:
        return "\033[32m {} {}\033[0m" .format(value, cont)
    elif float(value) < 0:
        return "\033[31m {} {}\033[0m" .format(value, cont)
    elif float(value) == 0:
        return "\033[33m {} {}\033[0m" .format(value, cont)

def normalize_float (value):
    return "{0:.2f}".format(float(value))

def count_percent (price_changing, summ):
    return normalize_float(price_changing / ((summ - price_changing) / 100))

def summ_portfolio (summ, position, eur_exchange_rate, usd_exchange_rate):
    if position['averagePositionPrice']['currency'] == "USD":
        return summ * usd_exchange_rate
    if position['averagePositionPrice']['currency'] == "EUR":
        return summ * eur_exchange_rate
    if position['averagePositionPrice']['currency'] == "RUB":
        return summ

def get_exchange_currency ():
    portfolio = client.get_portfolio(account_id=2039981838)['payload']['positions']
    usd_exchange_rate = client.get_market_orderbook(ticker="USD000UTSTOM", depth=1)['payload']['lastPrice']
    eur_exchange_rate = client.get_market_orderbook(ticker="EUR_RUB__TOM", depth=1)['payload']['lastPrice']
    return eur_exchange_rate, usd_exchange_rate

def print_table ():
    eur_exchange_rate, usd_exchange_rate = get_exchange_currency ()
    header = ['Тикер', 'Имя', 'Закупочная цена', 'Текущая цена', 'Количество', 'Cумма', 'Динамика', 'Процент']
    result = []
    summary = 0
    price_changing_portfolio = 0
    for position in portfolio:
        ticker = position['ticker']
        name = position['name'] 
        avg_price = position['averagePositionPrice']['value']
        curr_price = client.get_market_orderbook(figi=position['figi'], depth=1)['payload']['lastPrice']
        currency = position['averagePositionPrice']['currency']
        avg_price_curr = str(avg_price) + ' ' + currency
        curr_price_curr = str(curr_price) + ' ' + currency
        amount = position['balance']
        price_changing = position['expectedYield']['value']
        summ = curr_price * amount
        summ_curr = str(normalize_float(summ)) + ' ' + currency
        try:
            percent_changing = count_percent(price_changing, summ)
        except (ZeroDivisionError):
            percent_changing = "0"
        summary += summ_portfolio (summ, position, eur_exchange_rate, usd_exchange_rate)
        price_changing_portfolio += summ_portfolio (price_changing, position, eur_exchange_rate, usd_exchange_rate)
        result.append([ticker, name, avg_price_curr, curr_price_curr, amount, summ_curr, colorize(price_changing, currency), colorize(normalize_float(percent_changing), "%")])
    print (f"Портфель: Всего {normalize_float(summary)} {colorize(count_percent(price_changing_portfolio, summary), '%')}")
    print (tabulate(result, headers=header, tablefmt="grid"))

def time_to_str(datetime):
    return datetime.strftime("%Y-%m-%dT%H:%M:00+03:00")

def print_statistics ():
    now = datetime.today()
    today = datetime.combine(datetime.today().date(), time(0, 0))
    week = today - timedelta(days=7)
    month = today - timedelta(days=30)
    three_month = today - timedelta(days=90)
    year = today - timedelta(days=365)

    #today_statistics = client.get_operations(frm=time_to_str(today), to=time_to_str(now), account_id=2042625489)
    year_statistics = client.get_operations(frm=time_to_str(year),
                                            to=time_to_str(now),
                                            account_id=2042625489)['payload']['operations']
    divs = 0.0
    div_taxs = 0.0
    broker_commisions = 0.0
    buys = {}
    sells = {}
    reselling = 0.0
    print ('\n Статистика по оплатам за год: \n')
    for position, event in enumerate(year_statistics):
        if event['operationType'] == "Dividend":
            print (f"{event['date'].split('T')[0]} {client.get_ticker_by_figi(event['figi'])} Дивиденды Оплата: {colorize(event['payment'], event['currency'])}")
            divs += event['payment']
        elif event['operationType'] == "TaxDividend":
            print (f"{event['date'].split('T')[0]} {client.get_ticker_by_figi(event['figi'])} Дивиденды(н) Оплата: {colorize(event['payment'], event['currency'])}")
            div_taxs += event['payment']
        elif event['operationType'] == "BrokerCommission":
            print (f"{event['date'].split('T')[0]} {client.get_ticker_by_figi(event['figi'])} Коммисия брокеру Оплата: {colorize(event['payment'], event['currency'])}")
            broker_commisions += event['payment']
        #elif event['operationType'] == "PayIn":
            print (f"{event['date'].split('T')[0]} Внесено Оплата: {colorize(event['payment'], event['currency'])}")
        elif event['operationType'] == "Buy":
            print (f"{event['date'].split('T')[0]} {client.get_ticker_by_figi(event['figi'])} Куплено Оплата: {colorize(event['payment'], event['currency'])}")
            buys.setdefault(client.get_ticker_by_figi(event['figi']),[])
            buys[client.get_ticker_by_figi(event['figi'])].append(event['payment'])
        elif event['operationType'] == "Sell":
            print(f"{event['date'].split('T')[0]} Продано Оплата: {colorize(event['payment'], event['currency'])}")
            sells.setdefault(client.get_ticker_by_figi(event['figi']),[])
            sells[client.get_ticker_by_figi(event['figi'])].append(event['payment'])

    for k, v in sells.items():
        if buys.get(k):
            reselling = sum(v) + sum(buys[k])
            for pos in portfolio:
                if pos['ticker'] == k:
                    reselling += pos['averagePositionPrice']['value'] * pos['balance']

    print (f"""Итого: 
    Дивидендов получено: {colorize(divs, 'RUB')}
    Налогов с дивиденов уплачено: {colorize(div_taxs, 'RUB')}
    Коммисии брокера: {colorize(normalize_float(broker_commisions), 'RUB')}
    Доход от продажи бумаг: {colorize(reselling, 'RUB')}
    Общая доходность: {colorize(normalize_float(reselling + divs + (broker_commisions+div_taxs)), 'RUB')}
    """)


if __name__ == '__main__':
    print_table ()
    print_statistics()
