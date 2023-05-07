# https://www.youtube.com/watch?v=y65BZbNB0YA
# https://core.telegram.org/bots/webapps
import aiogram
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from aiogram.types.web_app_info import WebAppInfo
from aiogram.types import InputMediaPhoto
import json
import config
import main_controller
import attachments

bot = Bot(config.telegram_token)

dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    markup = types.ReplyKeyboardMarkup()
    markup.add(types.KeyboardButton('Меню', web_app=WebAppInfo(url=config.url_menu)))
    await message.answer(f'Привет, {message.from_user.username}!', reply_markup=markup)


@dp.message_handler(content_types=['web_app_data'])
async def web_app(message: types.Message):
    response = json.loads(message.web_app_data.data)
    await message.answer(response['action'])
    if response['action'] == 'calc':
        markup = types.ReplyKeyboardMarkup()
        await message.answer(main_controller.calc(markup))


@dp.message_handler(content_types='text')
async def check_text(message: types.Message):
    answer = main_controller.text_handler(message.text)
    if answer is not None:
        await message.answer(answer, parse_mode='HTML')


@dp.message_handler(content_types='photo')
async def photo_handler(message: types.Message):
    # https://github.com/aiogram/aiogram/issues/665
    await attachments.file_download(message)


executor.start_polling(dp)
