import pytest


@pytest.mark.asyncio
async def test_tinkoff_get_portfolio(app):
    async for obj in app:
        result = obj.market['tinkoff'].get_portfolio()
        assert result, "Can't get a portfolio from market"
        assert isinstance(result, dict), "Type of portfolio data not dict"


@pytest.mark.asyncio
async def test_tinkoff_search_ticker(app):
    async for obj in app:
        assert obj.market['tinkoff'].search_ticker("AAPL"), "Can't found ticker in market"


@pytest.mark.asyncio
async def test_tinkoff_brief_ticker_info(app):
    async for obj in app:
        result = await obj.market['tinkoff'].show_brief_ticker_info_by_id("AAPL", uid=738070069)
        assert result, "There is no any ticker info"
        assert isinstance(result, dict), "Ticker info isn't dict"


@pytest.mark.asyncio
async def test_tinkoff_summary_ticker_info(app):
    async for obj in app:
        result = await obj.show_summary_ticker_info("AAPL", uname="escading0", uid=738070069)
        assert result, "There is no any ticker info summary"
        assert isinstance(result, dict), "Ticker info summary isn't dict"


@pytest.mark.asyncio
async def test_get_username_tickers(app):
    async for obj in app:
        result = await obj.market['tinkoff'].get_username_tickers()
        assert result, "There is no any tickers for user"
        assert isinstance(result, dict), "Tickers for all users isn't dict"
