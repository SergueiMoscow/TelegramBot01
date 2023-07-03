from aiogram import Bot, Dispatcher, executor, types
import datetime

from sqlalchemy.orm import sessionmaker

import config
from models import Photo, engine


async def file_download(message: types.Message) -> None:
    """Downloads image from message and register it in database."""
    now = datetime.datetime.now()
    filename = now.strftime('%Y%m%d_%H%M%S_%f')
    _session = sessionmaker(bind=engine)
    session = _session()
    photo = Photo(
        user=message.from_user.username,
        file=filename,
        description=message.md_text
    )
    session.add(photo)
    session.commit()
    session.close()

    await message.photo[-1].download(
        destination_file=f'{config.save_path}{message.from_user.username}/{filename}.jpg',
        make_dirs=True)

    await message.answer(f'File downloaded {message.photo[-1].file_size} bytes')
