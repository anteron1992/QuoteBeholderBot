import requests
from qbot.logger import logger
from requests.exceptions import HTTPError

class TinvestAPI:
    """
    Класс для работы с OpenAPI 20.2 Тинькофф Инвестиции.
    """
    #####Приватные методы#####
    def __init__ (self, token):
        """
        Конструктор класса, забираем у пользователя токен и формируем заголовок запроса.
        """
        self.__token = token
        self.__url = "https://api-invest.tinkoff.ru/openapi/"
        self.__headers = {"accept": "application/json", "Authorization": f"Bearer {token}"}

    def __exec_req (self, url=None):
        """
        Внутренний метод запроса, возвращает результат в json формате.
        """
        try:
            req = requests.get(url, headers=self.__headers)
        except HTTPError as http_err:
            logger.error(f'HTTP error occurred: {http_err}')
            raise HTTPError (f'HTTP error occurred: {http_err}')
        except Exception as err:
            logger.error(f'Other HTTP error occurred: {err}')
            raise Exception (f'Other error occurred: {err}')
        else:
            if req.status_code == 401:
                logger.error("Unauthorized : HTTP 401")
                raise Exception("Unauthorized : HTTP 401")
            elif req.status_code == 500:
                logger.error("Инструмент или брокерский счет не найден : HTTP 500")
                raise Exception("Инструмент или брокерский счет не найден : HTTP 500")
            try:
                return req.json()
            except Exception as err2:
                logger.error("f'Ошибка {req} - {err2}'")
                raise Exception (f'Ошибка HTTP {req} - {err2}')

    def __format_time (self, time):
        try:
            return time.replace(":", "%3A").replace("+", "%2B")
        except Exception:
            return None

    ####REST API Тинькофф Инвестиции#####
    def get_user_accounts (self):
        """
        Получаение списка счетов пользователя, без атрибутов.
        """
        return self.__exec_req (self.__url + "user/accounts")

    def get_portfolio (self, account_id=None):
        """
        Получение состава портфеля, может принимать необязательный атрибут account_id, для
        указания id счёта пользователя, по умолчанию выводит состав основного брокерского счёта
        """
        url = self.__url + "portfolio"
        if account_id:
            url += f"?brokerAccountId={str(account_id)}"
        return self.__exec_req (url)

    def get_portfolio_currencies (self, account_id=None):
        """
        Получение валютных активов счёта, необязательный атрибут: account_id=<int/str>
        """
        url = self.__url + "portfolio/currencies"
        if account_id:
            url += f"?brokerAccountId={str(account_id)}"
        return self.__exec_req (url)

    def get_market_stocks (self):
        """
        Получение списка акций на рынке, без атрибутов.
        """
        return self.__exec_req (self.__url + "market/stocks")

    def get_market_bonds (self):
        """
        Получение списка облигаций на рынке, без атрибутов.
        """
        return self.__exec_req (self.__url + "market/bonds")

    def get_market_etfs (self):
        """
        Получение списка ETF на рынке, без атрибутов.
        """
        return self.__exec_req (self.__url + "market/etfs")

    def get_market_by_ticker (self, ticker):
        url = self.__url + "market/search/by-ticker"
        if ticker:
            url += f"?ticker={ticker}"
        return self.__exec_req (url)

    def get_operations (self, frm=None, to=None, figi=None, ticker=None, account_id=None):
        """
        Получение списка операций на рынке. Обязательные атрибуты: frm <time>, to <time>
        Формат времени: 2021-07-13T17:43:33+03:00
        Необязательные: figi=<str>, ticker=<str>, account_id=<int/str>
        """
        url = self.__url + "operations"
        url += f"?from={self.__format_time(frm)}&to={self.__format_time(to)}"

        if figi and not ticker:
            url += f"&figi={figi}"
        elif ticker and not figi:
            figi = self.get_market_by_ticker(ticker)["payload"]["instruments"][0]["figi"]
            url += f"&figi={figi}"
        elif figi and ticker:
            raise ValueError("Укажите или figi или ticker")
        if account_id:
            url += f"&brokerAccountId={str(account_id)}"
        return self.__exec_req(url)

    def get_market_by_figi (self, figi=None):
        """
        Поиск инструмента на рынке по figi. Обязательный атрибут: figi=<str>
        """
        url = self.__url + "/market/search/by-figi"
        if figi:
            url += f"?figi={figi}"
        return self.__exec_req (url)

    def get_ticker_by_figi (self, figi=None):
        """
        Поиск тикера на рынке по figi. Обязательный атрибут: figi=<str>
        """
        url = self.__url + "/market/search/by-figi"
        if figi:
            url += f"?figi={figi}"
        return self.__exec_req (url)['payload']['ticker']

    def get_market_orderbook (self, figi=None, ticker=None, depth=None):
        """
        Получение стакана по figi или ticker. Необязательный атрибут: depth=<int(1-20)>
        """
        url = self.__url + "market/orderbook"
        if figi and ticker:
            raise ValueError("Укажите или figi или ticker")
        elif depth not in range (1,21):
            raise ValueError("depth должен быть от 1 до 20")
        elif ticker:
            figi = self.get_market_by_ticker(ticker)["payload"]["instruments"][0]["figi"]
        url += f"?figi={figi}&depth={int(depth)}"
        return self.__exec_req(url)






