# Снять ограничение 30 дней в цикле !!!
import datetime

import requests
import bs4
from DbHelper import DbHelper as db

import ssl
ssl._create_default_https_context = ssl._create_unverified_context
BASE_URL = 'https://www.anekdot.ru/release/'
LATEST_UNREAD_DATE = 0
LATEST_UNREAD_INDEX = 1
MAX_ITEMS_PER_DAY = 5


class Anekdot:

    _user = None
    _table_user = 'anekdot_user'
    _table_items = 'anekdot'

    def __init__(self, user):
        db.connect()
        self._user = user

    def get_item(self, category: str) -> str:
        latest_unread = self._calc_latest_unread(category)
        row = db.select_one(
            table=self._table_items,
            fields=['an_id', 'text'],
            where=f"category='{category}' AND `date`='{latest_unread[LATEST_UNREAD_DATE]}' AND consecutive={latest_unread[LATEST_UNREAD_INDEX]}",
        )
        if row is None:
            url = self._get_url(category, latest_unread[LATEST_UNREAD_DATE])
            item = self._get_content(url, category, latest_unread)
        else:
            item = row['an_id'], row['text']
        self._register_read(category, latest_unread, item[0])
        return item[1]

    def _calc_latest_unread(self, category: str) -> tuple:
        category = category.lower()
        rows = db.select(
            table=self._table_user,
            where=f"`user`='{self._user}' AND `category`='{category}'",
            fields=['date', 'passed'],
            order=['`date` DESC']
        )
        read = {el['date']: el['passed'] for el in rows} if rows is not None else {}
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
        url_category = 'anekdot' if category.lower() == 'a' else 'story'
        return f'{BASE_URL}{url_category}/day/{date}/'

    @classmethod
    def _get_content(cls, url: str, category: str, latest_unread: tuple) -> tuple:
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
        where = f"`user`='{self._user}' AND date='{latest_unread[LATEST_UNREAD_DATE]}' AND category='{category}'"
        rows = db.select(
            table=self._table_user,
            fields=['an_ids'],
            where=where
        )
        if rows is not None and len(rows) > 0:
            read_ids = f"{rows[0]['an_ids']},{an_id}"
        else:
            read_ids = str(an_id)
        db.update_or_insert_one(
            table=self._table_user,
            fields=['user', 'date', 'category', 'passed', 'an_ids'],
            values=[
                self._user,
                latest_unread[LATEST_UNREAD_DATE],
                category.lower(),
                latest_unread[LATEST_UNREAD_INDEX],
                read_ids
            ],
            where=where
        )

    @classmethod
    def _save_in_db(cls, list_items, category: str, date: str) -> None:
        for counter in range(MAX_ITEMS_PER_DAY):
            # index +1 потому что 0й в заголовке
            an_id, text = cls.clear_item_from_tags(list_items[counter + 1])
            db.insert(
                table=cls._table_items,
                fields_list=['date', 'category', 'consecutive', 'an_id', 'text'],
                values_list=(date, category, counter, an_id, text)
            )
            counter += 1

    @staticmethod
    def clear_item_from_tags(item) -> tuple:
        text = item.find_all('div', 'text')[0].get_text()
        an_id = item['data-id']
        return an_id, text
