# Снять ограничение 30 дней в цикле !!!
import datetime

import requests
import bs4
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import sessionmaker

# from DbHelper import DbHelper as db

import ssl

from models import engine, AnekdotUser, Anekdot

ssl._create_default_https_context = ssl._create_unverified_context
BASE_URL = 'https://www.anekdot.ru/release/'
LATEST_UNREAD_DATE = 0
LATEST_UNREAD_INDEX = 1
MAX_ITEMS_PER_DAY = 5


class Handler:

    _user = None
    _table_user = 'anekdot_user'
    _table_items = 'anekdot'

    def __init__(self, user):
        self._user = user

    def get_item(self, category: str) -> str:
        """Returns item(anekdot or story) for display as message from bot"""
        latest_unread = self.calc_latest_unread(category)
        _session = sessionmaker(bind=engine)
        session = _session()
        row = session.query(Anekdot.an_id, Anekdot.text).\
            filter(Anekdot.category == category).\
            filter(Anekdot.date == latest_unread[LATEST_UNREAD_DATE]).\
            filter(Anekdot.consecutive == latest_unread[LATEST_UNREAD_INDEX]).\
            first()

        if row is None:
            url = self._get_url(category, latest_unread[LATEST_UNREAD_DATE])
            item = self._get_content(url, category, latest_unread)
        else:
            item = row.an_id, row.text
        self._register_read(category, latest_unread, item[0])
        return f'{item[1]}\n{latest_unread[LATEST_UNREAD_DATE]} ({latest_unread[LATEST_UNREAD_INDEX]})'

    def calc_latest_unread(self, category: str) -> tuple:
        """Calculates last unread item"""
        category = category.lower()
        _session = sessionmaker(bind=engine)
        session = _session()
        rows = session.query(AnekdotUser.date, AnekdotUser.passed).\
            filter(AnekdotUser.user == self._user,  AnekdotUser.category == category).\
            order_by(AnekdotUser.date.desc()).all()
        session.close()
        print(rows)
        # read = {read['date']: read['passed'] for el in rows} if rows is not None else {}
        read = {date: value for date, value in rows}
        mask = '%Y-%m-%d'
        now = datetime.datetime.now()
        yesterday = now - datetime.timedelta(days=1)
        counter = 0
        # Начинаем со вчерашнего дня, т.к. новые выходят в течение дня и их ещё может не быть.
        day_to_check = yesterday
        next_consecutive = 0
        print(f'Read: {read} (before while) cond: {str(day_to_check)[:10]} in read')
        while str(day_to_check)[:10] in read:
            print(f'While: {str(day_to_check)[:10]}, {next_consecutive}')
            if read[str(day_to_check)[:10]] < MAX_ITEMS_PER_DAY - 1:
                next_consecutive = read[str(day_to_check)[:10]] + 1
                break
            day_to_check = day_to_check - datetime.timedelta(days=1)
            counter += 1
            # Ограничиваем максимум 1000 дней, зачем старое читать? :)
            if counter > 1000:
                print(f'Counter {counter}')
                break

        # TODO: Не хватает обработки, если всё прочитано

        print(f'Next day: {day_to_check}, consec: {next_consecutive}')
        return day_to_check.strftime(mask), next_consecutive

    @staticmethod
    def _get_url(category: str, date: str) -> str:
        """Constructs URL string to download items"""
        url_category = 'anekdot' if category.lower() == 'a' else 'story'
        return f'{BASE_URL}{url_category}/day/{date}/'

    @classmethod
    def _get_content(cls, url: str, category: str, latest_unread: tuple) -> tuple:
        """Downloads page, parses it to items and saves to database"""
        date = latest_unread[LATEST_UNREAD_DATE]
        index = latest_unread[LATEST_UNREAD_INDEX]
        print(f'url(get_content): {url}')
        html = requests.get(url)
        parsed_html = bs4.BeautifulSoup(html.text, "html.parser")
        # replace <br> with \n
        delimiter = '\n'
        for line_break in parsed_html.findAll('br'):
            line_break.replaceWith(delimiter)
        list_items = parsed_html.find_all('div', 'topicbox')
        cls._save_in_db(list_items, category, date)
        an_id, text = cls.clear_item_from_tags(list_items[index+1])
        return an_id, text

    def _register_read(self, category: str, latest_unread: tuple, an_id: int) -> None:
        """Marks as read item for user"""
        _session = sessionmaker(bind=engine)
        with _session() as session:
            try:
                anekdot_user = session.query(AnekdotUser). \
                    filter(AnekdotUser.user == self._user). \
                    filter(AnekdotUser.date == latest_unread[LATEST_UNREAD_DATE]). \
                    filter(AnekdotUser.category == category). \
                    one_or_none()
            except NoResultFound:
                anekdot_user = None

            if anekdot_user is None:
                anekdot_user = AnekdotUser(
                    user=self._user,
                    date=latest_unread[LATEST_UNREAD_DATE],
                    category=category,
                    an_ids=str(an_id),
                    passed=latest_unread[LATEST_UNREAD_INDEX]
                )
                session.add(anekdot_user)
            else:
                anekdot_user.an_ids = f"{anekdot_user.an_ids},{an_id}"
                anekdot_user.passed = latest_unread[LATEST_UNREAD_INDEX]

            session.commit()
            session.close()

    @classmethod
    def _save_in_db(cls, list_items, category: str, date: str) -> None:
        """Saves downloaded items to database"""
        _session = sessionmaker(bind=engine)
        with _session() as session:
            for counter, item in enumerate(list_items[1:MAX_ITEMS_PER_DAY + 1], start=1):
                an_id, text = cls.clear_item_from_tags(item)
                anekdot = Anekdot(
                    date=date,
                    category=category,
                    consecutive=counter-1,
                    an_id=an_id,
                    text=text
                )
                session.add(anekdot)
            session.commit()
            session.close()

    @staticmethod
    def clear_item_from_tags(item) -> tuple:
        """Parses item deleting all HTML tags"""
        text = item.find_all('div', 'text')[0].get_text()
        an_id = item['data-id']
        return an_id, text


if __name__ == '__main__':
    print(Anekdot.calc_latest_unread('A', 'aaa'))
