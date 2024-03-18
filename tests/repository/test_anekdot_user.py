import pytest

from app.db.engine import AsyncSession
from app.repository.anekdot_user import find_last_unread_anekdot


@pytest.mark.usefixtures('apply_migrations')
async def test_find_last_unread_anekdot(created_multiple_anekdot_users):
    for condition in range(len(created_multiple_anekdot_users)):
        if condition == 1:
            pass
        anekdot_user = created_multiple_anekdot_users['records'][condition]
        estimated_values = created_multiple_anekdot_users['estimated_values'][condition]
        async with AsyncSession() as session:
            result = await find_last_unread_anekdot(
                session, anekdot_user.user, anekdot_user.category
            )
            assert result == estimated_values
