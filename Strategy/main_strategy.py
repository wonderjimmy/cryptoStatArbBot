import warnings
warnings.simplefilter(action="ignore", category=FutureWarning)

from func_get_symbols import get_tradable_symbols
from func_prices_json import store_price_history
from func_plot_trends import plot_trends
from config_strategy_api import prices_json_file_name
from func_cointegration import get_cointegrated_pairs
import pandas as pd
import json

""" strategy """

if __name__ == "__main__":
    """
    # step 1 - get list of symbols
    print("Getting symbols...")
    sym_response = get_tradable_symbols()

    # step 2 - construct and save price history
    print("Constructing and saving price data to JSON...")
    if len(sym_response) > 0:
        store_price_history(sym_response)

    # step 3 - find cointegrated pairs
    print("Calculating co-integration...")
    with open(prices_json_file_name) as json_file:
        price_data = json.load(json_file)
        if len(price_data) > 0:
            cointegrated_pairs = get_cointegrated_pairs(price_data)

    """
    # step 4 - plot trends and save for back-testing
    print("Plotting trends...")
    symbol_1 = "DOGEUSDT"
    symbol_2 = "GSTUSDT"
    with open(prices_json_file_name) as json_file:
        price_data = json.load(json_file)
        if len(price_data) > 0:
            plot_trends(symbol_1, symbol_2, price_data)

    print("Done.")
