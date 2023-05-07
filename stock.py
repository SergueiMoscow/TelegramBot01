import pandas as pd
from tinkoff.invest import CandleInterval, Client, SecurityTradingStatus, InstrumentIdType
from tinkoff.invest.utils import now
from datetime import timedelta
import json
from tinkoff.invest.utils import quotation_to_decimal
from tinkoff.invest.services import InstrumentsService
import config
from aiogram import types
from aiogram.types.web_app_info import WebAppInfo


def get_info(figi):
    instrument = get_by_figi(figi)
    last_price = get_last_price(figi)
    result = f'{instrument.instrument.ticker} {instrument.instrument.name}    <b>{last_price}</b>\n'
    result += f'<a href="{config.url_instrument}">Подробнее</a>'
    return result


def find_instruments(query: str) -> pd.DataFrame:
    with Client(config.tinkoff_token) as client:
        r = client.instruments.find_instrument(query=query)
        df = pd.DataFrame(r.instruments)
        # print(f'find_instruments 1st df: {df}')
        if df.empty:
            return None
        df = df[df['class_code'].isin(['TQBR', 'SPBFUT'])][['figi', 'ticker', 'name']]
        # df.to_csv('instr.csv')
        # print(f'<{query}>')
        # print(df)
        # print(f'find_indtruments shape {df.shape[0]}')
        if df.shape[0] > 1:
            if df[df['ticker'] == query].shape[0] != 0:
                df = df[df['ticker'] == query]
        get_candles(df['figi'].iloc[0])
        return df


def get_by_figi(figi: str):
    with Client(config.tinkoff_token) as client:
        try:
            i = client.instruments.get_instrument_by(id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_FIGI, id=figi)
        except:
            i = {'message': f'not found {figi}', 'figi': f'not found {figi}'}
        print(i)
        return i


def get_last_prices(figi: list):
    with Client(config.tinkoff_token) as client:
        last_price = (client.market_data.get_last_prices([figi]))
        last_price = quotation_to_decimal(last_price)
        return last_price


def get_last_price(figi: str) -> float:
    candles = get_candles(figi)
    max_time = candles['time'].max()
    close_price = candles[candles['time'] == max_time]['close']
    close_price = close_price[list(close_price.keys())[0]]
    last_price = float(f"{close_price['units']}.{close_price['nano']}")
    return last_price


def get_candles(figi, days_before=1) -> pd.DataFrame:
    candles = []
    with Client(config.tinkoff_token) as client:
        for candle in client.get_all_candles(
            figi=figi,  # "BBG004730N88",
            from_=now() - timedelta(days=days_before),
            interval=CandleInterval.CANDLE_INTERVAL_DAY,
        ):
            candles.append(candle)
            # print(type(candle), candle)
    df = pd.DataFrame(candles)
    df.to_csv(f'candles_{figi}.csv')
    return df
