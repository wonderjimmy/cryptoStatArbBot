"""
    API documentation
    https://bybit-exchange.github.io/docs/linear/#t-introduction
"""

# API imports
from pybit import usdt_perpetual
from Config.constant import *

# config variables
mode = MODE_TEST
ticker_1 = "BTCUSDT"
ticker_2 = "ETHUSDT"
signal_positive_ticker = ticker_2
signal_negative_ticker = ticker_1

# may be auto configured below:
rounding_ticker_1 = 2
rounding_ticker_2 = 2
quantity_rounding_ticker_1 = 5
quantity_rounding_ticker_2 = 4

limit_order_basis = True
tradeable_capital_usdt = 50000   # to be spilt between pair
stop_loss_fail_safe = 0.02      # 0.15
signal_trigger_thresh = 0.5     # must be above 0

timeframe = 60
kline_limit = 200
z_score_window = 21

# Live API
api_key_mainnet = ""
api_secret_mainnet = ""

# Test API
api_key_testnet = "uY912nePlXjWGLvTlO"
api_secret_testnet = "eMDmVch8Iy0menzqTjijNYbQCXKwpymR3rUz"

# Selected API
api_key = api_key_testnet if mode == MODE_TEST else api_key_mainnet
api_secret = api_secret_testnet if mode == MODE_TEST else api_secret_mainnet

# Selected URL
api_url = "https://api-testnet.bybit.com" if mode == MODE_TEST else "https://api.bybit.com"
ws_public_url = "wss://stream-testnet.bybit.com/realtime_public" if mode == "test" else "wss://stream.bybit.com/realtime_public"

# session activation
session_public = usdt_perpetual.HTTP(api_url)
session_private = usdt_perpetual.HTTP(api_url, api_key=api_key, api_secret=api_secret)

# leverage factor
buy_leverage = 1
sell_leverage = 1

# other conrtol parameters

# If one position is filled but another position is still active, after this wait time the counter position will
# be covered using market order instead
wait_min_for_market_order = 3

is_debug = 1

cointegrated_pairs_file_name = "2_cointegrated_pairs.csv"
