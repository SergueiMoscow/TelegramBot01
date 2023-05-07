import stock


def calc(string: str):
    try:
        result = eval(string)
    except:
        result = None
    return result


def text_handler(text: str):
    answer = calc(text)
    if answer is not None:
        return answer
    text = text.replace('/', '')
    instruments = stock.find_instruments(text)
    if instruments is None:
        return None
    if instruments.shape[0] > 1:
        instruments['ticker'] = '/' + instruments['ticker']
        return f'Уточните запрос: \n{instruments}'
    figi = instruments.iloc[0]['figi']
    info = stock.get_info(figi)
    return info


