from qbot.db.database import Database
from qbot.tests.data.data_market import TICKER_INFO_FALSE, \
    TICKER_INFO_TRUE, TICKER_INFO_BRIEF_NEW, TICKER_INFO_BRIEF_OLD, NEWS_NEW, NEWS_OLD
import pytest


@pytest.mark.asyncio
async def test_database_ticker_checking():
    db = Database(tests=True)
    assert await db.check_ticker("SBER", uid=176549646) == True, "Not found existing ticker in db"
    assert await db.check_ticker("TEST", uid=176549646) == False, "Non existing ticker has been found in db"


@pytest.mark.asyncio
async def test_database_user_creation():
    db = Database(tests=True)
    assert await db.add_new_user_to_db("Test", uid=123456789) == True, "Can't add new user in db"
    assert await db.check_user(uid=123456789) == True, "Existing user hasn't been found in db"
    assert await db.delete_user_from_db("Test", uid=123456789) == True, "Can't delete existing user from db"
    assert await db.check_user(uid=123456789) == False, "Non existing user has been found in db"


@pytest.mark.asyncio
async def test_ticker_subscription():
    db = Database(tests=True)
    assert await db.subscribe_on_new_ticker(
        "Anteron", uid=176549646, ticker_info=TICKER_INFO_FALSE, price=123
    ) == True, "Can't subscribe on new ticker"
    assert await db.subscribe_on_new_ticker(
        "Anteron", uid=176549646, ticker_info=TICKER_INFO_FALSE, price=123
    ) == False, "Ticker exist in db, but was tried to add again"
    assert await  db.delete_subscribed_ticker(
        "TEST", uname="Anteron", uid=176549646
    ) == True, "Can't unsubscribe on exist ticker"
    assert await  db.delete_subscribed_ticker(
        "TEST", uname="Anteron", uid=176549646
    ) == False, "Ticker don't exist in db, but was tried to delete again"


@pytest.mark.asyncio
async def test_get_list_of_subscribes():
    db = Database(tests=True)
    result = await db.show_list_of_subscribes(uname="Anteron", uid=176549646)
    assert result, "There is no any tickers in list of subscribes"
    assert isinstance(result, list), "List of subscribes isn't type list"


@pytest.mark.asyncio
async def test_get_list_of_subscribes_by_id():
    db = Database(tests=True)
    result = await db.show_list_of_subscribes_by_id(uid=176549646)
    assert result, "There is no any tickers in list of subscribes"
    assert isinstance(result, list), "List of subscribes isn't type list"


@pytest.mark.asyncio
async def test_get_user_list():
    db = Database(tests=True)
    assert await db.show_usernames(), "There is no any user in db"


@pytest.mark.asyncio
async def test_get_brief_ticker_info_by_id():
    db = Database(tests=True)
    result = await db.get_ticker_info_by_id(TICKER_INFO_TRUE, uid=176549646, price=123)
    assert result, "There is no any info about ticker"
    assert isinstance(result, dict), "Info about ticker isn't type dict"


@pytest.mark.asyncio
async def test_get_summary_tickers_by_id():
    db = Database(tests=True)
    result = await db.get_summary_tickers_by_id(TICKER_INFO_TRUE, uname="Anteron", uid=176549646, price=123)
    assert result, "There is no any summary info about ticker"
    assert isinstance(result, dict), "Summary info about ticker isn't type dict"


@pytest.mark.asyncio
async def test_override_price():
    db = Database(tests=True)
    assert await db.get_price_by_ticker("AAPL", uid=176549646) == 123.0, "Checking old price"
    assert await db.override_price(TICKER_INFO_BRIEF_NEW, uid=176549646) == True, "Override not happened"
    assert await db.get_price_by_ticker("AAPL", uid=176549646) == 170.95, "Checking new price"
    assert await db.override_price(TICKER_INFO_BRIEF_OLD, uid=176549646) == True, "Override not happened"


@pytest.mark.asyncio
async def test_get_time_of_last_news():
    db = Database(tests=True)
    assert await db.get_time_of_last_news("SBER") == '8 июля в 08:45', "Failed try to get time of last news"


@pytest.mark.asyncio
async def test_update_news_info():
    db = Database(tests=True)
    assert await db.update_news_info("SBER", NEWS_NEW) == True, "Failed to update news info in db"
    assert await db.get_time_of_last_news("SBER") == '1 января в 00:00', "Failed try to get time of last news"
    assert await db.update_news_info("SBER", NEWS_OLD) == True, "Failed to update news info in db"
    assert await db.get_time_of_last_news("SBER") == '8 июля в 08:45', "Failed try to get time of last news"
