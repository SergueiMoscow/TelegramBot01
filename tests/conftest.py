import random
from datetime import datetime, timedelta

import pytest
from sqlalchemy import text as sa_text

from alembic import command
from alembic.config import Config
from app.db.engine import Session
from app.db.models import Anekdot, AnekdotUser
from app.settings import ROOT_DIR, settings


@pytest.fixture
def apply_migrations():
    assert 'TEST' in settings.DATABASE_SCHEMA.upper(), 'Попытка использовать не тестовую схему.'

    alembic_cfg = Config(str(ROOT_DIR / 'alembic.ini'))
    alembic_cfg.set_main_option('script_location', str(ROOT_DIR / 'alembic'))
    command.downgrade(alembic_cfg, 'base')
    command.upgrade(alembic_cfg, 'head')

    yield command, alembic_cfg

    command.downgrade(alembic_cfg, 'base')

    with Session() as session:
        session.execute(sa_text(f'DROP SCHEMA IF EXISTS {settings.DATABASE_SCHEMA} CASCADE;'))
        session.commit()


@pytest.fixture
def get_random_date() -> str:
    year_from = 2000
    year_to = 2024
    start_date = datetime(year_from, 1, 1)
    end_date = datetime(year_to, 12, 31)

    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates + 1)

    random_date = start_date + timedelta(days=random_number_of_days)
    return random_date.strftime('%Y-%m-%d')


@pytest.fixture
def create_anekdot(faker, get_random_date):  # pylint: disable=redefined-outer-name
    def _create(category: str | None = None):
        if category is None:
            category = random.choice(['a', 's'])
        anekdot = Anekdot(
            date=get_random_date,
            category=category,
            consecutive=faker.random_int(min=0, max=settings.MAX_ITEMS_PER_DAY),
            an_id=faker.random_int(),
            text=faker.paragraph(),
        )
        return anekdot

    return _create


@pytest.fixture
def create_anekdot_user(faker, get_random_date):  # pylint: disable=redefined-outer-name
    def _create(
        user: str | None = None,
        category: str | None = None,
        date: str | None = None,
        passed: int | None = None,
    ):
        if category is None:
            category = random.choice(['a', 's'])
        if user is None:
            user = faker.name()
        if date is None:
            date = get_random_date
        if passed is None:
            passed = (faker.random_int(min=0, max=settings.MAX_ITEMS_PER_DAY),)
        anekdot_user = AnekdotUser(
            user=user,
            date=date,
            category=category,
            passed=passed,
            an_ids=faker.sentence(),
        )
        return anekdot_user

    return _create


@pytest.fixture
def created_anekdot(create_anekdot):  # pylint: disable=redefined-outer-name
    with Session() as session:
        anekdot = create_anekdot()
        session.add(anekdot)
        session.commit()
    return anekdot


@pytest.fixture
def created_anekdot_user(create_anekdot_user):  # pylint: disable=redefined-outer-name
    with Session() as session:
        anekdot_user = create_anekdot_user()
        session.add(anekdot_user)
        session.commit()
    return anekdot_user


@pytest.fixture
def created_multiple_anekdot_users(
    faker, create_anekdot_user
):  # pylint: disable=(redefined-outer-name, too-many-statements, unused-argument)
    """Создаёт записи для теста поиска:
    0. Вчерашний день прочитан, далее ничего нет
    1. Вчерашний день прочитан частично, далее ничего нет
    2. Вчерашний прочитан, позавчерашний частично
    3. 2 последних прочитаны, дальше ничего нет
    4. 2 последних прочитаны, далее перерыв, далее полностью прочитан
    5. 2 последних прочитаны, далее перерыв, далее частично прочитан
    """
    users_count = 6  # Количество условий проверки
    users = [faker.name() for _ in range(users_count)]
    date_format = '%Y-%m-%d'
    today = datetime.now()
    anekdot_users = []
    estimated_values = []
    for condition in range(6):
        user = users[condition]
        category = random.choice(['a', 's'])
        if condition in [0, 2, 3, 4, 5]:
            # Вчерашний день прочитан, далее ничего нет
            current_date = today + timedelta(days=-1)
            anekdot_users.append(
                AnekdotUser(
                    user=user,
                    date=current_date.strftime(date_format),
                    category=category,
                    passed=settings.MAX_ITEMS_PER_DAY,
                )
            )
        if condition == 1:
            # Вчерашний день прочитан частично, далее ничего нет
            current_date = today + timedelta(days=-1)
            anekdot_users.append(
                AnekdotUser(
                    user=user,
                    date=current_date.strftime(date_format),
                    category=category,
                    passed=faker.random_int(min=1, max=settings.MAX_ITEMS_PER_DAY - 1),
                )
            )
        if condition == 2:
            # Вчерашний прочитан, позавчерашний частично
            current_date = today + timedelta(days=-2)
            anekdot_users.append(
                AnekdotUser(
                    user=user,
                    date=current_date.strftime(date_format),
                    category=category,
                    passed=faker.random_int(min=1, max=settings.MAX_ITEMS_PER_DAY - 1),
                )
            )
        if condition in [3, 4, 5]:
            # 2 последних прочитаны, дальше ничего нет
            current_date = today + timedelta(days=-2)
            anekdot_users.append(
                AnekdotUser(
                    user=user,
                    date=current_date.strftime(date_format),
                    category=category,
                    passed=settings.MAX_ITEMS_PER_DAY,
                )
            )
        if condition == 4:
            # 2 последних прочитаны, далее перерыв, далее полностью прочитан
            current_date = today + timedelta(days=-faker.random_int(min=2, max=10))
            anekdot_users.append(
                AnekdotUser(
                    user=user,
                    date=current_date.strftime(date_format),
                    category=category,
                    passed=settings.MAX_ITEMS_PER_DAY,
                )
            )
        if condition == 5:
            # 2 последних прочитаны, далее перерыв, далее частично прочитан
            current_date = today + timedelta(days=-faker.random_int(min=2, max=10))
            anekdot_users.append(
                AnekdotUser(
                    user=user,
                    date=current_date.strftime(date_format),
                    category=category,
                    passed=faker.random_int(min=1, max=settings.MAX_ITEMS_PER_DAY - 1),
                )
            )

    # 0. Вчерашний день прочитан, далее ничего нет
    estimated_values.append({'date': (today + timedelta(days=-2)).strftime(date_format), 'next': 1})
    # 1. Вчерашний день прочитан частично, далее ничего нет
    estimated_values.append(
        {
            'date': (today + timedelta(days=-1)).strftime(date_format),
            'next': anekdot_users[1].passed + 1,
        }
    )
    # 2. Вчерашний прочитан, позавчерашний частично
    estimated_values.append(
        {
            'date': (today + timedelta(days=-2)).strftime(date_format),
            'next': anekdot_users[1].passed + 1,
        }
    )
    # 3. 2 последних прочитаны, дальше ничего нет
    estimated_values.append({'date': (today + timedelta(days=-3)).strftime(date_format), 'next': 1})
    # 4. 2 последних прочитаны, далее перерыв, далее полностью прочитан
    estimated_values.append({'date': (today + timedelta(days=-3)).strftime(date_format), 'next': 1})
    # 5. 2 последних прочитаны, далее перерыв, далее частично прочитан
    estimated_values.append({'date': (today + timedelta(days=-3)).strftime(date_format), 'next': 1})
    # Добавляем в таблицу:
    with Session() as session:
        session.bulk_save_objects(anekdot_users)
        session.commit()
    return {'records': anekdot_users, 'estimated_values': estimated_values}
