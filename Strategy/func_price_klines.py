"""
interval: 60, "D"
from: integer from timestamp in seconds
limit: max 200
"""

from config_strategy_api import session
from config_strategy_api import timeframe
from config_strategy_api import kline_limit
import datetime
import time

# get start time
time_start_date = 0
if timeframe == 60:
    time_start_date = datetime.datetime.now() - datetime.timedelta(hours=kline_limit)
if timeframe == "D":
    time_start_date = datetime.datetime.now() - datetime.timedelta(days=kline_limit)
time_start_seconds = int(time_start_date.timestamp())

# get historical prices
def get_price_klines(symbol):
    prices = session.query_mark_price_kline(
        symbol = symbol,
        interval = timeframe,
        limit = kline_limit,
        from_time = time_start_seconds
    )

    time.sleep(0.1)

    if len(prices["result"]) != kline_limit:
        return []
    else:
        return prices["result"]

