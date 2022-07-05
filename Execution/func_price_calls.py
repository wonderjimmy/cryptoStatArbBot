from config_execution_api import session_public, timeframe, kline_limit
from func_calculations import extract_close_prices
import datetime, time


# get trade liquidity for ticker
def get_ticker_trade_liquidity(ticker):
    # get trade history
    trades = session_public.public_trading_records(
        symbol=ticker,
        limits=50
    )

    # get the average liquidity
    quantity_list = []
    if "result" in trades.keys():
        for trade in trades["result"]:
            quantity_list.append(trade["qty"])
    if len(quantity_list) > 0:
        average_liquidity = sum(quantity_list) / len(quantity_list)
        res_trade_price = float(trades["result"][0]["price"])
        return average_liquidity, res_trade_price
    return 0, 0


# get trade liquidity for ticker
def get_ticker_trade_liquidity_vwap(ticker):
    # get trade history
    trades = session_public.public_trading_records(
        symbol=ticker,
        limits=50
    )

    # get the average liquidity
    amount_list = []
    quantity_list = []
    if "result" in trades.keys():
        for trade in trades["result"]:
            quantity_list.append(trade["qty"])
            amount_list.append(trade["qty"] * trade["price"])
    if len(amount_list) > 0:
        average_liquidity = sum(quantity_list) / len(quantity_list)
        vwap_trade_price = float(sum(amount_list) / sum(quantity_list))
        return average_liquidity, vwap_trade_price
    return 0, 0


# get start time
def get_timestamps():
    time_start_date = 0
    time_next_date = 0
    now = datetime.datetime.now()
    if timeframe == 60:
        time_start_date = now - datetime.timedelta(hours=kline_limit)
        time_next_date = now + datetime.timedelta(hours=1)
    if timeframe == "D":
        time_start_date = now - datetime.timedelta(days=kline_limit)
        time_next_date = now + datetime.timedelta(days=1)
    time_start_seconds = int(time_start_date.timestamp())
    time_now_seconds = int(now.timestamp())
    time_next_seconds = int(time_next_date.timestamp())
    return time_start_seconds, time_now_seconds, time_next_seconds


# get historical prices (klines)
def get_price_klines(ticker):
    # get prices
    time_start_seconds, _, _ = get_timestamps()
    prices = session_public.query_mark_price_kline(
        symbol=ticker,
        interval=timeframe,
        limit=kline_limit,
        from_time=time_start_seconds
    )

    # manage API calls
    time.sleep(0.1)

    # return prices output
    if len(prices["result"]) != kline_limit:
        return []
    return prices["result"]


# get latest klines
def get_latest_klines(ticker_1, ticker_2):
    series_1 = []
    series_2 = []
    prices_1 = get_price_klines(ticker_1)
    prices_2 = get_price_klines(ticker_2)

    if len(prices_1) > 0:
        series_1 = extract_close_prices(prices_1)
    if len(prices_2) > 0:
        series_2 = extract_close_prices(prices_2)

    return series_1, series_2
