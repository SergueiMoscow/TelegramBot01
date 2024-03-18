import datetime
import os

from aiogram import types

from app.db.engine import AsyncSession
from app.db.models import Photo
from app.settings import settings


async def file_download(message: types.Message) -> None:
    """Downloads image from message and register it in database."""
    now = datetime.datetime.now()
    filename = now.strftime('%Y%m%d_%H%M%S_%f')
    photo = Photo(user=message.from_user.username, file=filename, description=message.md_text)
    with AsyncSession() as session:
        session.add(photo)
        session.commit()

    await message.photo[-1].download(
        destination_file=os.path.join(
            settings.SAVE_PATH, message.from_user.username, filename + '.jpg'
        ),
        make_dirs=True,
    )

    await message.answer(f'File downloaded {message.photo[-1].file_size} bytes')
