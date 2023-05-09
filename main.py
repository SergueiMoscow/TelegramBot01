# https://www.youtube.com/watch?v=y65BZbNB0YA
# https://core.telegram.org/bots/webapps
from aiogram import Bot, Dispatcher, executor, types
from PIL import Image
import json
import config
import main_controller
import attachments
from io import BytesIO

bot = Bot(config.telegram_token)

dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    markup = types.ReplyKeyboardMarkup()
    # markup.add(types.KeyboardButton('Меню', web_app=WebAppInfo(url=config.url_menu)))
    await message.answer(f'Привет, {message.from_user.username}!\n{config.instruction}', reply_markup=markup)


@dp.message_handler(content_types=['web_app_data'])
async def web_app(message: types.Message):
    response = json.loads(message.web_app_data.data)
    await message.answer(response['action'])
    if response['action'] == 'calc':
        markup = types.ReplyKeyboardMarkup()
        await message.answer(main_controller.calc(markup))


@dp.message_handler(content_types='text')
async def check_text(message: types.Message):
    answer = main_controller.text_handler(message.text, message.from_user.username)
    if answer is not None:
        if isinstance(answer, str):
            await message.answer(answer, parse_mode='HTML')
        elif isinstance(answer, Image.Image):
            bio = BytesIO()
            bio.name = 'image.jpeg'
            answer.save(bio, 'JPEG')
            bio.seek(0)
            await bot.send_photo(message.from_user.id, photo=bio)
        else:
            await message.answer(type(answer))


@dp.message_handler(content_types='photo')
async def photo_handler(message: types.Message):
    await attachments.file_download(message)

if __name__ == '__main__':
    executor.start_polling(dp)
