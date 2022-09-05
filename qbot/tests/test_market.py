from qbot.market.tinvest import Tinvest
import pytest
from qbot.tests.data.data_market import PORTFOLIO
from qbot.app.app import application as app


def test_tinkoff_get_portfolio():
    tinkoff = app(tests=True).market['tinkoff']
    result = tinkoff.get_portfolio()
    assert result, "Can't get a portfolio from market"
    assert isinstance(result, dict), "Type of portfolio data not dict"


def test_tinkoff_search_ticker():
    tinkoff = app(tests=True).market['tinkoff']
    assert tinkoff.search_ticker("AAPL"), "Can't found ticker in market"


@pytest.mark.asyncio
async def test_tinkoff_subscribtion_portfolio():
    tinkoff = app(tests=True).market['tinkoff']
    assert await tinkoff.delete_subscribe_portfolio(
        PORTFOLIO, uname="@Anteron", uid=176549646
    ) == True, "Problem with deleting of portfolio subscription, perhaps user not found in db"
    assert await tinkoff.db.check_ticker("SBER", uid=176549646) == False, "Ticker has been found after deletion"
    assert await tinkoff.subscribe_portfolio(
        PORTFOLIO, uname="@Anteron", uid=176549646
    ) == True, "Problem with subscribing of portfolio, perhaps user not found in db"
    assert await tinkoff.db.check_ticker("SBER", uid=176549646) == True, "Ticker hasn't been found after addition"


@pytest.mark.asyncio
async def test_tinkoff_brief_ticker_info():
    tinkoff = app(tests=True).market['tinkoff']
    result = await tinkoff.show_brief_ticker_info_by_id("AAPL", uid=176549646)
    assert result, "There is no any ticker info"
    assert isinstance(result, dict), "Ticker info isn't dict"


@pytest.mark.asyncio
async def test_tinkoff_summary_ticker_info():
    tinkoff = app(tests=True).market['tinkoff']
    result = await tinkoff.show_summary_ticker_info("AAPL", uname="@Anteron", uid=176549646)
    assert result, "There is no any ticker info summary"
    assert isinstance(result, dict), "Ticker info summary isn't dict"


@pytest.mark.asyncio
async def test_get_username_tickers():
    tinkoff = app(tests=True).market['tinkoff']
    result = await tinkoff.get_username_tickers()
    assert result, "There is no any tickers for user"
    assert isinstance(result, dict), "Tickers for all users isn't dict"
