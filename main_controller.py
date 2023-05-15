import stock
import Anekdot


def calc(string: str):
    """Check if and calculate if string can be evaluated"""
    try:
        result = eval(string)
    except:
        result = None
    return result


def text_handler(text: str, username: str):
    """Handler text input"""
    answer = calc(text)
    if answer is not None:
        return answer
    text = text.replace('/', '')
    # Проверка на запрос анекдотов / историй
    if text.lower() == 'a' or text.lower() == 's':
        an = Anekdot.Anekdot(username)
        item = an.get_item(text.lower())
        return f'{item}\n/a   /s'
    instruments = stock.find_instruments(text)
    if instruments is None:
        return f'Can\'t find {text}'
    if instruments.shape[0] > 1:
        instruments['ticker'] = '/' + instruments['ticker']
        return f'Уточните запрос: \n{instruments}'
    print(f'main_controller: 31: {instruments}')
    figi = instruments.iloc[0]['figi']
    info = stock.get_info(figi)
    return info


