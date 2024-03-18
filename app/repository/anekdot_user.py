from datetime import datetime, timedelta
from typing import Dict

from sqlalchemy import and_
from sqlalchemy.future import select

from app.db.engine import AsyncSession
from app.db.models import AnekdotUser
from app.settings import settings


async def find_last_unread_anekdot(
    session: AsyncSession, user_id: str, category: str = 'a'
) -> Dict[str, int]:

    # Получить время на вчерашний день
    yesterday = datetime.now() - timedelta(days=1)

    # Сформировать запрос для получения последнего прочитанного анекдота категории
    query = (
        select(AnekdotUser).where(
            and_(AnekdotUser.user == user_id, AnekdotUser.category == category)
        )
    ).order_by(AnekdotUser.date.desc())

    # Выполнить запрос
    last_read_anekdots = (await session.execute(query)).scalars().all()

    if last_read_anekdots:
        # Получить дату последнего прочитанного анекдота
        last_date = datetime.strptime(last_read_anekdots[0].date, settings.DATE_FORMAT)
        for anekdot in last_read_anekdots:
            anekdot_date = datetime.strptime(anekdot.date, settings.DATE_FORMAT)
            if (last_date - anekdot_date).days > 1:
                return {
                    'date': (last_date - timedelta(days=1)).strftime(settings.DATE_FORMAT),
                    'next': 1,
                }
            last_date = anekdot_date
            if anekdot.passed < settings.MAX_ITEMS_PER_DAY:
                return {'date': anekdot.date, 'next': anekdot.passed + 1}
        return {'date': (last_date - timedelta(days=1)).strftime(settings.DATE_FORMAT), 'next': 1}
    else:
        # Если анекдоты не прочитаны, вернуть вчерашний день и первый элемент
        return {'date': yesterday.strftime(settings.DATE_FORMAT), 'next': 1}


async def register_read(
    session: AsyncSession, user: str, date: str, category: str, read_items: int
) -> int:
    query = select(AnekdotUser).where(
        and_(AnekdotUser.user == user, AnekdotUser.date == date, AnekdotUser.category == category)
    )
    result = await session.execute(query)
    anekdot_user = result.scalars().first()
    if anekdot_user:
        anekdot_user.passed = read_items
        return 1
    anekdot_user = AnekdotUser(
        user=user,
        date=date,
        category=category,
        passed=read_items,
    )
    session.add(anekdot_user)
    return 1
