from sqlalchemy import and_, desc, select

from app.db.engine import AsyncSession
from app.db.models import Anekdot, AnekdotUser
from app.settings import settings


async def get_anekdot_by_date_and_consecutive(
    session: AsyncSession,
    category: str,
    date: str,
    consecutive: int,
) -> Anekdot:
    result = await session.execute(
        select(Anekdot).where(
            and_(
                Anekdot.category == category,
                Anekdot.date == date,
                Anekdot.consecutive == consecutive,
            )
        )
    )

    return result.scalars().first()


async def get_anekdot_user_read(session: AsyncSession, user: str, category: str):
    result = (
        session.query(AnekdotUser.date, AnekdotUser.passed)
        .filter(AnekdotUser.user == user, AnekdotUser.category == category)
        .order_by(desc(AnekdotUser.date))
        .all()
    )
    return result


async def save_anekdot(
    session: AsyncSession, date: str, category: str, consecutive: int, an_id: int, text: str
):
    anekdot = Anekdot(
        date=date,
        category=category,
        consecutive=consecutive,
        an_id=an_id,
        text=text,
    )
    session.add(anekdot)
