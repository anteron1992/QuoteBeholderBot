TICKER_INFO_FALSE = {'currency': 'USD',
                              'figi': 'BBG000000000',
                              'isin': 'US0000000000',
                              'lot': 1,
                              'minPriceIncrement': 0.01,
                              'name': 'Test ticker',
                              'ticker': 'TEST',
                              'type': 'Stock'}

TICKER_INFO_TRUE = {'currency': 'USD',
                              'figi': 'BBG000000000',
                              'isin': 'US0000000000',
                              'lot': 1,
                              'minPriceIncrement': 0.01,
                              'name': 'Apple',
                              'ticker': 'AAPL',
                              'type': 'Stock'}

TICKER_INFO_BRIEF_NEW = {'ticker': 'AAPL', 'last_price': '123', 'curr_price': 170.95, 'diff': 38.98}

TICKER_INFO_BRIEF_OLD = {'ticker': 'AAPL', 'last_price': '123', 'curr_price': 123.00, 'diff': 38.98}

NEWS_NEW = {'time': '1 января в 00:00', 'header': 'Test news'}
NEWS_OLD = {'time': '8 июля в 08:45', 'header': 'Сбербанк. Отбились'}

PORTFOLIO = {'payload': {'positions': [{'averagePositionPrice': {'currency': 'RUB',
                                                     'value': 166.7},
                            'balance': 730.0,
                            'expectedYield': {'currency': 'RUB',
                                              'value': -58801.2},
                            'figi': 'BBG004730JJ5',
                            'instrumentType': 'Stock',
                            'isin': 'RU000A0JR4A1',
                            'lots': 73,
                            'name': 'Московская Биржа',
                            'ticker': 'MOEX'},
                           {'averagePositionPrice': {'currency': 'RUB',
                                                     'value': 2109.6},
                            'balance': 44,
                            'expectedYield': {'currency': 'RUB',
                                              'value': -8309.4},
                            'figi': 'BBG006L8G4H1',
                            'instrumentType': 'Stock',
                            'isin': 'NL0009805522',
                            'lots': 44,
                            'name': 'Yandex',
                            'ticker': 'YNDX'},
                           {'averagePositionPrice': {'currency': 'RUB',
                                                     'value': 4015},
                            'balance': 12,
                            'expectedYield': {'currency': 'RUB',
                                              'value': -385.5},
                            'figi': 'BBG004731032',
                            'instrumentType': 'Stock',
                            'isin': 'RU0009024277',
                            'lots': 12,
                            'name': 'ЛУКОЙЛ',
                            'ticker': 'LKOH'},
                           {'averagePositionPrice': {'currency': 'RUB',
                                                     'value': 39.135},
                            'balance': 2300.0,
                            'expectedYield': {'currency': 'RUB',
                                              'value': -23338},
                            'figi': 'BBG004S681M2',
                            'instrumentType': 'Stock',
                            'isin': 'RU0009029524',
                            'lots': 23,
                            'name': 'Сургутнефтегаз - привилегированные акции',
                            'ticker': 'SNGSP'},
                           {'averagePositionPrice': {'currency': 'RUB',
                                                     'value': 290.21},
                            'balance': 660.0,
                            'expectedYield': {'currency': 'RUB',
                                              'value': -74705.7},
                            'figi': 'BBG004730RP0',
                            'instrumentType': 'Stock',
                            'isin': 'RU0007661625',
                            'lots': 66,
                            'name': 'Газпром',
                            'ticker': 'GAZP'},
                           {'averagePositionPrice': {'currency': 'RUB',
                                                     'value': 70.05},
                            'balance': 690.0,
                            'expectedYield': {'currency': 'RUB',
                                              'value': -2235.6},
                            'figi': 'BBG004S68B31',
                            'instrumentType': 'Stock',
                            'isin': 'RU0007252813',
                            'lots': 69,
                            'name': 'АЛРОСА',
                            'ticker': 'ALRS'},
                           {'averagePositionPrice': {'currency': 'RUB',
                                                     'value': 1246.3},
                            'balance': 37,
                            'expectedYield': {'currency': 'RUB',
                                              'value': -19472},
                            'figi': 'BBG004S68BH6',
                            'instrumentType': 'Stock',
                            'isin': 'RU000A0JP7J7',
                            'lots': 37,
                            'name': 'ПИК',
                            'ticker': 'PIKK'},
                           {'averagePositionPrice': {'currency': 'RUB',
                                                     'value': 307.75},
                            'balance': 510.0,
                            'expectedYield': {'currency': 'RUB',
                                              'value': -93235},
                            'figi': 'BBG004730N88',
                            'instrumentType': 'Stock',
                            'isin': 'RU0009029540',
                            'lots': 51,
                            'name': 'Сбер Банк',
                            'ticker': 'SBER'},
                           {'averagePositionPrice': {'currency': 'RUB',
                                                     'value': 890.5},
                            'balance': 53,
                            'expectedYield': {'currency': 'RUB',
                                              'value': 21945},
                            'figi': 'BBG00JXPFBN0',
                            'instrumentType': 'Stock',
                            'isin': 'US98387E2054',
                            'lots': 53,
                            'name': 'ГДР X5 RetailGroup',
                            'ticker': 'FIVE'}]},
 'status': 'Ok',
 'trackingId': '5ae7aef3f8ffd9ed'}