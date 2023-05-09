from aiogram import Bot, Dispatcher, executor, types
import datetime
import config
import DbHelper


async def file_download(message: types.Message) -> None:
    now = datetime.datetime.now()
    db = DbHelper.DbHelper()
    filename = now.strftime('%Y%m%d_%H%M%S_%f')

    db.insert(
        'photos',
        fields_list=['user', 'added', 'file'],
        values_list=(message.from_user.username, now.strftime('%Y-%m-%d %H:%M:%S'), filename)
    )

    await message.photo[-1].download(
        destination_file=f'{config.save_path}{message.from_user.username}/{filename}.jpg',
        make_dirs=True)

    await message.answer(f'File downloaded {message.photo[-1].file_size} bytes')
