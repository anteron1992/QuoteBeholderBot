# QuoteBeholderBot
Телеграм бот позволяет подписаться на биржевые бумаги. 
1) Если происходит резкое изменение цены - бот уведомит об этом.
2) Периодически бот рассылает новости по бумагам в подписке

Официальный бот: https://t.me/QuoteBeholderBot

### Инструкция для пользователей

1) Переходим по ссылке выше и подписываемся на бота
2) Пишем ему `/start` после чего бот готов к работе
3) Для того чтобы подписаться на нужную бумагу указываем `/subscribe` и нужный тикер (или список):
4) Для того чтобы отписаться от бумаг, все тоже самое только с `/unsubscribe`:
5) Для просмотра своего списка тикеров `/show_subscribes`
6) Информацию о конкретном тикете можно взглянуть через `/show_ticker`:
7) :lock: В боте так же имеется `/subscribe_portfolio` и `/unsubscribe_portfolio`
Данные функции позволят на автоматически подписываться на акции из вашего в портфеля в Тинькофф Инвестиции: возможность пока не доступна. В разработке

### Инструкция для форков
1) Клонируем на машину репозиторий
2) Создаем в репозитории auth.env:
    * TINKOFF_TOKEN - Токен для Тинькофф API (подойдет для sandbox)
    * TINKOFF_ACCOUNT_ID - ID вашего аккаунта в Тинькофф Инвестиции
    * TELE_TOKEN - Токен вашего Телеграм бота
3) Заходим в каталог и создаем виртуальное окружение `python3.9 -m venv ./venv`
4) Активируем его `source venv/bin/activate`

:warning: Чтобы каждый раз не активировать venv, можете добавить себе его в bashrc:

```
echo "source ~/QuoteBeholderBot/venv/bin/activate" >> ~/.bashrc
exec bash
```
5) Устанавливаем все необходимые пакеты и зависимости `pip install .`
6) Запускаем `pytest .` в `qbot/tests`, проверяем что все ок и готово к работе
(сломается один шаг на `AssertionError: DB file is not exist`, это не страшно, файл БД создастся после первого запуска приложения)
7) Запускаем `qbot/quotebeholder.py`

Логи приложения будут складываться в `/var/log/quotebeholder/`
##### Настройки
Доступные настройки лежат в `qbot/config/default-config.yml`

* ticker_interval - Через сколько будет производится проверка цены тикера (5 мин по-умолчанию)
* news_interval - Через сколько будет производится проверка новостей по тикеру (5 мин по-умолчанию)
* reaction_percent - Уровень реакции на изменения цены в % (2% по-умолчанию)
* exceptions - Исключения для тикеров, новости которых не удается распознать. 

Новости берутся с сайта по ссылке  https://bcs-express.ru/category?tag=[ticker]

Но иногда tag не равен названию тикера.

Например валютная пара Евро-Рубль имеет тикер `EUR_RUB__TOM`, а `tag` для новостей по доллару и евро - `eur-usd`.

В конфиге это можно указать так:
```
exceptions:
  EUR_RUB__TOM: eur-usd
```
Информацию о том что бот не смог распознать тикер можно будет увидеть в `/var/log/quotebeholder/quotebeholder.log`
