from aiogram import Bot, Dispatcher, executor, types
from PIL import Image
import json
import config
import main_controller
import attachments
from io import BytesIO

bot = Bot(config.telegram_token)

dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def start(message: types.Message):
    """Returns start and help text"""
    markup = types.ReplyKeyboardMarkup()
    #markup.add(types.KeyboardButton('Меню', web_app=WebAppInfo(url=config.url_menu)))
    await message.answer(f'Привет, {message.from_user.username}!\n{config.instruction}', reply_markup=markup)


@dp.message_handler(content_types='text')
async def check_text(message: types.Message):
    """Processes text from the user"""
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
            await message.answer(answer)


@dp.message_handler(content_types='photo')
async def photo_handler(message: types.Message):
    """Processes image from the user"""
    await attachments.file_download(message)

if __name__ == '__main__':
    executor.start_polling(dp)
    # executor.start_polling(dp, skip_updates=True, on_startup=setup_bot_commands)
