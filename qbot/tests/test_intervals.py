from qbot.interval_actions import Interval_actions
from qbot.tests.data.data_market import TICKER_INFO_BRIEF_NEW, TICKER_INFO_BRIEF_OLD, NEWS_NEW, NEWS_OLD
from asyncio import sleep
import pytest


class mock_bot:
    @staticmethod
    async def send_message(*args, **kwargs):
        await sleep(0.1)


@pytest.mark.asyncio
async def test_ticker_polling(app):
    async for app_instance in app:
        obj = Interval_actions(app_instance)
        assert await obj.ticker_polling(mock_bot) is None, "Polling don't work"


@pytest.mark.asyncio
async def test_news_polling(app):
    async for app_instance in app:
        obj = Interval_actions(app_instance)
        assert await obj.news_polling(mock_bot) is None, "Polling don't work"
