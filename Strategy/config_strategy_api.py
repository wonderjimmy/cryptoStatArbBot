"""
    API documentation
    https://bybit-exchange.github.io/docs/linear/#t-introduction
"""

# API imports
from pybit import usdt_perpetual

# Config
mode = "test"
timeframe = 60
kline_limit = 200
z_score_window = 21
prices_json_file_name = "1_prices_list.json"
cointegrated_pairs_file_name = "2_cointegrated_pairs.csv"
# backtest_pair = "3_backtest_file.csv"

# Live API
api_key_mainnet = ""
api_secret_mainnet = ""

# Test API
api_key_testnet = "uY912nePlXjWGLvTlO"
api_secret_testnet = "eMDmVch8Iy0menzqTjijNYbQCXKwpymR3rUz"

# Selected API
api_key = api_key_testnet if mode == "test" else api_key_mainnet
api_secret = api_secret_testnet if mode == "test" else api_secret_mainnet

# Selected URL
api_url = "https://api-testnet.bybit.com" if mode == "test" else "https://api.bybit.com"

# Session activation
session = usdt_perpetual.HTTP(api_url)

# Number of pairs for preparing backtest files
number_of_backtest_pair = 100

# # Web socket connection
# usdt_perpetual.WebSocket
#
# ws = usdt_perpetual.WebSocket(
#     test=True,
#     api_key=api_key,
#     api_secret=api_secret,
# )