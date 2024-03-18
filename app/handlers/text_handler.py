import logging

from app.handlers import stock
from app.handlers.AnekdotHandler import AnekdotHandler
from app.settings import settings

logger = logging.getLogger(__name__)
logging.basicConfig(filename=settings.LOG_FILE, encoding='utf-8', level=logging.DEBUG)


def calc(string: str):
    """Check if and calculate if string can be evaluated"""
    try:
        result = eval(string)
    except Exception:
        result = None
    return result


async def text_handler(text: str, username: str):
    """Handler text input"""
    answer = calc(text)
    if answer is not None:
        return answer
    text = text.replace('/', '')
    # Проверка на запрос анекдотов / историй
    if text.lower() == 'a' or text.lower() == 's':
        an = AnekdotHandler(username)
        item = await an.get_item(text.lower())
        return f'{item}\n/a   /s'
    instruments = stock.find_instruments(text)
    if instruments is None:
        return f'Can\'t find {text}'
    if instruments.shape[0] > 1:
        instruments['ticker'] = '/' + instruments['ticker']
        return f'Уточните запрос: \n{instruments}'
    logger.warning(f'main_controller: 31: {instruments}')
    figi = instruments.iloc[0]['figi']
    info = stock.get_info(figi)
    return info
