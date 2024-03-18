import logging
from datetime import datetime, timedelta

import pandas as pd
from tinkoff.invest import CandleInterval, Client, InstrumentIdType
from tinkoff.invest.utils import now, quotation_to_decimal

from app.handlers.draw import draw_price
from app.settings import settings

logger = logging.getLogger(__name__)
logging.basicConfig(filename=settings.LOG_FILE, encoding='utf-8', level=logging.DEBUG)


def get_info(figi):
    """Returns image with instrument data"""
    instrument = get_by_figi(figi)
    min_price_increment = quotation_to_decimal(instrument.instrument.min_price_increment)
    last_price = get_last_prices(figi)
    candles = get_candles(figi, days_before=1)
    # if the day off is on the stock exchange, then there are no candles
    try:
        price_open = quotation_to_decimal(candles[len(candles) - 1].open)
    except Exception:
        price_open = last_price

    logger.info(f'type min_price_inc:{type(min_price_increment)}')
    logger.info(instrument)
    logger.info(f'Increment: {min_price_increment}')
    result = f'{instrument.instrument.ticker} {instrument.instrument.name}\n'
    result += f'open: {beautify_price(float(price_open), float(min_price_increment))}\n'
    result += f'current: {beautify_price(float(last_price), float(min_price_increment))}\n'
    result += f'change: {get_change_string(float(price_open), float(last_price))}'
    image = draw_price(
        ticker=instrument.instrument.ticker,
        name=instrument.instrument.name,
        price=beautify_price(last_price, min_price_increment),
        open=beautify_price(price_open, min_price_increment),
        change_string=get_change_string(price_open, last_price),
    )
    logger.info(f'result type: {type(image)}')
    return image
    # return result


def find_instruments(query: str) -> pd.DataFrame:
    """Searchs instrument by name or ticker in stocks and futures"""
    with Client(settings.TINKOFF_TOKEN) as client:
        r = client.instruments.find_instrument(query=query.upper())
        df = pd.DataFrame(r.instruments)
        logger.info(f'find_instruments 1st df: {query.upper()}: {df}')
        if df.empty:
            return None
        df = df[df['class_code'].isin(['TQBR', 'SPBFUT'])][['figi', 'ticker', 'name']]
        if df.shape[0] > 1:
            if df[df['ticker'] == query.upper()].shape[0] != 0:
                df = df[df['ticker'] == query.upper()]
        return df


def get_by_figi(figi: str):
    """Searchs and returns instrument by FIGI (financial Instrument Global Identifier"""
    with Client(settings.TINKOFF_TOKEN) as client:
        try:
            i = client.instruments.get_instrument_by(
                id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_FIGI, id=figi
            )
        except Exception:
            i = {'message': f'not found {figi}', 'figi': f'not found {figi}'}
        return i


def get_last_prices(figi: list) -> float:
    """Get last price of stocks or feature"""
    with Client(settings.TINKOFF_TOKEN) as client:
        last_price = client.market_data.get_last_prices(figi=[figi])
        last_price = quotation_to_decimal(last_price.last_prices[0].price)
        return float(last_price)


# Another way to get last price
# def get_last_price(figi: str) -> float:
#     candles = get_candles(figi)
#     max_time = candles['time'].max()
#     close_price = candles[candles['time'] == max_time]['close']
#     close_price = close_price[list(close_price.keys())[0]]
#     last_price = float(f"{close_price['units']}.{close_price['nano']}")
#     return last_price


def get_candles(figi, days_before=1) -> list:
    """Get last day candle"""
    candles = []
    with Client(settings.TINKOFF_TOKEN) as client:
        for candle in client.get_all_candles(
            figi=figi,  # "BBG004730N88",
            from_=now() - timedelta(days=days_before),
            interval=CandleInterval.CANDLE_INTERVAL_DAY,
        ):
            candles.append(candle)
    # df = pd.DataFrame(candles)
    # df.to_csv(f'candles_{figi}.csv')
    return candles


# another way to get candles:
def get_candles2(figi, days_before=1) -> list:
    with Client(settings.TINKOFF_TOKEN) as client:
        r = client.market_data.get_candles(
            figi=figi,
            from_=datetime.utcnow() - timedelta(days=days_before),
            to=datetime.utcnow(),
            interval=CandleInterval.CANDLE_INTERVAL_DAY,
        )
    return r.candles


def get_change_string(open: float, price: float):
    """calculates the percentage of price change per day
    and for the string for image ex: +1.2%, -2.3%"""
    one_percent = open / 100
    change = abs(price - open) / one_percent
    result = '+' if price > open else '-'
    result += f'{change:.2f}%'
    return result


def count_end_zeros(string: str) -> int:
    """Calculate end zeros in stiring"""
    return min((i for i, c in enumerate(string[::-1], 0) if c != '0'), default=1)


def beautify_price(price: float, min_price_increment: float):
    """Forms a string with the price with the required number of decimal places,
    depending on the instrument"""
    float(min_price_increment)
    logger.debug(f'beautify: {min_price_increment}')
    if min_price_increment > 1:
        logger.debug('>0')
        return str(f'{price:.0f}')
    elif min_price_increment >= 0.01:
        logger.debug('beautify >=0.01')
        return str(f'{price:0.2f}')
    else:
        logger.debug('beautify else')
        s_price = str(price)
        return s_price[: len(s_price) - count_end_zeros(s_price)]
