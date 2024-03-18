from datetime import datetime, timedelta

import pytest
from sqlalchemy import select

from app.db.engine import AsyncSession
from app.db.models import Anekdot, AnekdotUser
from app.handlers.AnekdotHandler import AnekdotHandler
from app.settings import settings


class AnekdotHandlerForTest(AnekdotHandler):
    @classmethod
    async def get_content(cls, *args, **kwargs):
        return await cls._get_content(*args, **kwargs)

    @classmethod
    async def get_url(cls, *args, **kwargs):
        return await cls._get_url(*args, **kwargs)


@pytest.mark.usefixtures('apply_migrations')
async def test_get_content(faker):
    yesterday = (datetime.now() - timedelta(days=1)).strftime(settings.DATE_FORMAT)
    category = 'a'
    user = faker.name()
    index = 1
    handler = AnekdotHandlerForTest(user)
    url = await handler.get_url('a', yesterday)
    assert '/day/' in url
    content = await handler.get_content(url, category, yesterday, index)
    assert isinstance(content, tuple)
    async with AsyncSession() as session:
        result = await session.execute(select(Anekdot))
        anekdot_list = result.scalars().all()
    assert int(content[0]) == anekdot_list[index - 1].an_id
    assert content[1] == anekdot_list[index - 1].text
    assert len(anekdot_list) == settings.MAX_ITEMS_PER_DAY


@pytest.mark.usefixtures('apply_migrations')
async def test_get_item(faker):
    yesterday = (datetime.now() - timedelta(days=1)).strftime(settings.DATE_FORMAT)
    user = faker.name()
    handler = AnekdotHandlerForTest(user)
    item = await handler.get_item('a')
    index = 1
    async with AsyncSession() as session:
        result = await session.execute(select(Anekdot))
        anekdot_list = result.scalars().all()
        result = await session.execute(select(AnekdotUser))
        anekdot_user_list = result.scalars().all()
    assert item is not None
    assert len(anekdot_list) == settings.MAX_ITEMS_PER_DAY
    assert anekdot_list[0].text == item[: len(anekdot_list[index - 1].text)]
    assert anekdot_user_list[0].passed == index
    assert anekdot_user_list[0].user == user
    assert anekdot_user_list[0].date == yesterday
