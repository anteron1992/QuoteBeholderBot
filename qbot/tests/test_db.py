from qbot.tests.data.data_market import TICKER_INFO_FALSE, \
    TICKER_INFO_TRUE, TICKER_INFO_BRIEF_NEW, TICKER_INFO_BRIEF_OLD, NEWS_NEW, NEWS_OLD
import pytest


@pytest.mark.asyncio
async def test_database_ticker_checking(app):
    async for obj in app:
        assert await obj.db.check_ticker("AAPL", uid=738070069) == True, "Not found existing ticker in db"
        assert await obj.db.check_ticker("QBFS", uid=422568345) == False, "Non existing ticker has been found in db"


@pytest.mark.asyncio
async def test_database_user_creation(app):
    async for obj in app:
        assert await obj.db.add_new_user_to_db("spam0eggs", uid=123456789) == True, "Can't add new user in db"
        assert await obj.db.check_user(uid=123456789) == True, "Existing user hasn't been found in db"
        assert await obj.db.delete_user_from_db("spam0eggs", uid=123456789) == True, "Can't delete existing user from db"
        assert await obj.db.check_user(uid=123456789) == False, "Non existing user has been found in db"


@pytest.mark.asyncio
async def test_ticker_subscription(app):
    async for obj in app:
        assert await obj.db.subscribe_on_new_ticker(
            "fbelfit4", uid=620028642, ticker_info=TICKER_INFO_FALSE, price=123
        ) == True, "Can't subscribe on new ticker"
        assert await obj.db.subscribe_on_new_ticker(
            "fbelfit4", uid=620028642, ticker_info=TICKER_INFO_FALSE, price=123
        ) == False, "Ticker exist in db, but was tried to add again"
        assert await obj.db.delete_subscribed_ticker(
            "TEST", uname="fbelfit4", uid=620028642
        ) == True, "Can't unsubscribe on exist ticker"
        assert await obj.db.delete_subscribed_ticker(
            "TEST", uname="fbelfit4", uid=620028642
        ) == False, "Ticker don't exist in db, but was tried to delete again"


@pytest.mark.asyncio
async def test_get_list_of_subscribes(app):
    async for obj in app:
        result = await obj.db.show_list_of_subscribes(uname="fbelfit4", uid=620028642)
        assert result, "There is no any tickers in list of subscribes"
        assert isinstance(result, list), "List of subscribes isn't type list"


@pytest.mark.asyncio
async def test_get_list_of_subscribes_by_id(app):
    async for obj in app:
        result = await obj.db.show_list_of_subscribes_by_id(uid=620028642)
        assert result, "There is no any tickers in list of subscribes"
        assert isinstance(result, list), "List of subscribes isn't type list"


@pytest.mark.asyncio
async def test_get_user_list(app):
    async for obj in app:
        assert await obj.db.show_usernames(), "There is no any user in db"


@pytest.mark.asyncio
async def test_get_brief_ticker_info_by_id(app):
    async for obj in app:
        result = await obj.db.get_ticker_info_by_id(TICKER_INFO_TRUE, uid=738070069, price=587.76)
        assert result, "There is no any info about ticker"
        assert isinstance(result, dict), "Info about ticker isn't type dict"


@pytest.mark.asyncio
async def test_get_summary_tickers_by_id(app):
    async for obj in app:
        result = await obj.db.get_summary_tickers_by_id(TICKER_INFO_TRUE, uname="escading0", uid=738070069, price=123)
        assert result, "There is no any summary info about ticker"
        assert isinstance(result, dict), "Summary info about ticker isn't type dict"


@pytest.mark.asyncio
async def test_override_price(app):
    async for obj in app:
        assert await obj.db.get_price_by_ticker("YNDX", uid=653509547) == 196.67, "Checking old price"
        assert await obj.db.override_price(TICKER_INFO_BRIEF_NEW, uid=653509547) == True, "Override not happened"
        assert await obj.db.get_price_by_ticker("YNDX", uid=653509547) == 570.95, "Checking new price"
        assert await obj.db.override_price(TICKER_INFO_BRIEF_OLD, uid=653509547) == True, "Override not happened"


@pytest.mark.asyncio
async def test_get_time_of_last_news(app):
    async for obj in app:
        assert await obj.db.get_time_of_last_news("GAZP") == '27 ноября в 00:18', "Failed try to get time of last news"


@pytest.mark.asyncio
async def test_update_news_info(app):
    async for obj in app:
        assert await obj.db.update_news_info("FIVE", NEWS_NEW, '1 января в 00:00') == True, "Failed to update news info in db"
        assert await obj.db.get_time_of_last_news("FIVE") == '1 января в 00:00', "Failed try to get time of last news"
        assert await obj.db.update_news_info("FIVE", NEWS_OLD, '15 апреля в 11:38') == True, "Failed to update news info in db"
        assert await obj.db.get_time_of_last_news("FIVE") == '15 апреля в 11:38', "Failed try to get time of last news"
        assert await obj.db.update_news_info("TEST", NEWS_NEW, 'new') == True, "Failed to update new news info in db"
        assert await obj.db.get_time_of_last_news("TEST") == '1 января в 00:00', "Failed try to get time of last news"
        assert await obj.db.delete_news_from_db("TEST") == True, "Failed try delete test ticker"

