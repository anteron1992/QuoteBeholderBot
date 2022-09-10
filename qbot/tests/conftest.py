import pytest
from qbot.app.application import application


@pytest.fixture(scope='session')
async def app():
    obj = application(tests=True)
    await obj.db.init()
    yield obj
    # await obj.db.close_pool()
