import asyncio
import os
import typing

import httpx
import pytest
from asgi_lifespan import LifespanManager
from starlette.types import ASGIApp

os.environ["TESTING"] = "True"
os.environ["DEBUG"] = "False"


@pytest.fixture(scope="session")
def event_loop() -> typing.Iterator[asyncio.AbstractEventLoop]:
    """
    Redefine from pytest-asyncio, as the default fixture is function-scoped.
    """
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def app() -> typing.AsyncIterator[ASGIApp]:
    import server

    async with LifespanManager(server.app):
        yield server.app


@pytest.fixture(scope="session")
async def client(app: ASGIApp) -> typing.AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(app=app) as client:
        yield client


@pytest.fixture(scope="session")
async def silent_client(app: ASGIApp) -> typing.AsyncIterator[httpx.AsyncClient]:
    transport = httpx.ASGITransport(app, raise_app_exceptions=False)
    async with httpx.AsyncClient(transport=transport) as client:
        yield client
