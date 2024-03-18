# Снять ограничение 30 дней в цикле !!!
import logging
import os
import ssl
from typing import Tuple

import bs4
import requests

from app.db.engine import AsyncSession
from app.repository.anekdot import get_anekdot_by_date_and_consecutive, save_anekdot
from app.repository.anekdot_user import find_last_unread_anekdot, register_read
from app.settings import ROOT_DIR

# from DbHelper import DbHelper as db


logger = logging.getLogger(__name__)
logging.basicConfig(
    filename=os.path.join(ROOT_DIR, 'debug.log'), encoding='utf-8', level=logging.DEBUG
)


ssl._create_default_https_context = ssl.create_default_context()  # ._create_unverified_context
BASE_URL = 'https://www.anekdot.ru/release/'
MAX_ITEMS_PER_DAY = 5


class AnekdotHandler:

    _user = None
    _table_user: str = 'anekdot_user'
    _table_items: str = 'anekdot'

    def __init__(self, user):
        self._user = user
        self._latest_unread_date: str = ''
        self._latest_unread_consecutive: int = -1
        self._category: str = ''

    async def get_item(self, category: str) -> str:
        self._category = category.lower()
        """Returns item(anekdot or story) for display as message from bot"""
        self._latest_unread_date, self._latest_unread_consecutive = await self.calc_latest_unread()
        log(f'Latest unread: {self._latest_unread_date} - {self._latest_unread_consecutive}')
        async with AsyncSession() as session:
            last_unread_anekdot = await get_anekdot_by_date_and_consecutive(
                session, category, self._latest_unread_date, self._latest_unread_consecutive
            )
        if last_unread_anekdot:
            item = last_unread_anekdot.an_id, last_unread_anekdot.text
        else:
            url = await self._get_url(category, self._latest_unread_date)
            item = await self._get_content(
                url, self._category, self._latest_unread_date, self._latest_unread_consecutive
            )
        await self._register_read()
        return f'{item[1]}\n{self._latest_unread_date} ({self._latest_unread_consecutive})'

    async def calc_latest_unread(self) -> Tuple[str, int]:
        """Calculates last unread item"""
        async with AsyncSession() as session:
            last_unread = await find_last_unread_anekdot(session, self._user, self._category)
        return last_unread['date'], last_unread['next']

    @staticmethod
    async def _get_url(category: str, date: str) -> str:
        """Constructs URL string to download items"""
        url_category = 'anekdot' if category.lower() == 'a' else 'story'
        return f'{BASE_URL}{url_category}/day/{date}/'

    @classmethod
    async def _get_content(cls, url: str, category: str, date: str, index: int) -> tuple:
        """Downloads page, parses it to items and saves to database"""
        logger.info(f'url(_get_content): {url}')
        html = requests.get(url)
        parsed_html = bs4.BeautifulSoup(html.text, 'html.parser')
        # replace <br> with \n
        delimiter = '\n'
        for line_break in parsed_html.findAll('br'):
            line_break.replaceWith(delimiter)
        list_items = parsed_html.find_all('div', 'topicbox')
        await cls._save_in_db(list_items, category, date)
        an_id, text = cls.clear_item_from_tags(list_items[index])
        return an_id, text

    async def _register_read(self) -> None:
        """Marks as read item for user"""
        async with AsyncSession() as session:
            await register_read(
                session,
                self._user,
                self._latest_unread_date,
                self._category,
                self._latest_unread_consecutive,
            )
            await session.commit()

    @classmethod
    async def _save_in_db(cls, list_items, category: str, date: str) -> None:
        """Saves downloaded items to database"""
        async with AsyncSession() as session:
            for counter, item in enumerate(list_items[1 : MAX_ITEMS_PER_DAY + 1], start=1):
                an_id, text = cls.clear_item_from_tags(item)
                await save_anekdot(
                    session,
                    date=date,
                    category=category,
                    consecutive=counter,
                    an_id=int(an_id),
                    text=text,
                )
            await session.commit()

    @staticmethod
    def clear_item_from_tags(item) -> tuple:
        """Parses item deleting all HTML tags"""
        text = item.find_all('div', 'text')[0].get_text()
        an_id = item['data-id']
        return an_id, text


def log(string: str):
    logging.basicConfig(
        filename='debug.log',
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s',
    )
    logging.info(string)


if __name__ == '__main__':
    h = AnekdotHandler('Serguei_Sushkov')
    logger.info(h.calc_latest_unread('s'))
    logger.info(h.get_item('s'))
