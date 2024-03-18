import pytest

from app.db.engine import AsyncSession
from app.repository.anekdot import (
    get_anekdot_by_date_and_consecutive,
)


@pytest.mark.usefixtures('apply_migrations')
async def test_get_anekdot_by_date_and_consecutive(created_anekdot):
    async with AsyncSession() as session:
        result = await get_anekdot_by_date_and_consecutive(
            session,
            created_anekdot.category,
            created_anekdot.date,
            created_anekdot.consecutive,
        )
    assert result is not None
    assert result.text == created_anekdot.text
