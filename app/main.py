import asyncio
import logging
import sys
from io import BytesIO

from aiogram import Bot, Dispatcher, F, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from PIL import Image

from app.handlers import attachments, text_handler
from app.settings import settings

dp = Dispatcher()

INSTRUCTION = """/a - анекдот
            /s - история
            Цены на акции/фьючерсы МосБиржи, например:
            /SBER Сбербанк
            /GAZP - Газпром
            и т.д."""


@dp.message(CommandStart())
async def start(message: types.Message):
    """Returns start and help text"""
    await message.answer(f'Привет, {message.from_user.username}!\n{INSTRUCTION}')


# pylint disable=too-many-nested-blocks
@dp.message(F.text)
async def check_text(message: types.Message):
    """Processes text from the user"""
    answer = await text_handler.text_handler(message.text, message.from_user.username)
    if answer is not None:  # pylint: disable=too-many-nested-blocks
        if isinstance(answer, str):
            if len(answer) > 4096:
                for x in range(0, len(answer), 4096):
                    await message.answer(answer[x : x + 4096], parse_mode='HTML')
            else:
                await message.answer(answer, parse_mode='HTML')
        elif isinstance(answer, Image.Image):
            bio = BytesIO()
            bio.name = 'image.jpeg'
            answer.save(bio, 'JPEG')
            bio.seek(0)
            await message.send_photo(message.from_user.id, photo=bio)
        else:
            if len(answer) > 4096:
                for x in range(0, len(answer), 4096):
                    await message.answer(answer[x : x + 4096])
            else:
                await message.answer(answer)


@dp.message(F.photo)
async def photo_handler(message: types.Message):
    """Processes image from the user"""
    await attachments.file_download(message)


async def main() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(settings.TELEGRAM_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
