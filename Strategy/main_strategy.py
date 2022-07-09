import warnings
warnings.simplefilter(action="ignore", category=FutureWarning)

from func_get_symbols import get_tradable_symbols
from func_prices_json import store_price_history
from func_plot_trends import analyse_pair
from config_strategy_api import prices_json_file_name, cointegrated_pairs_file_name, number_of_backtest_pair
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
    # step 4 - create the first 10 pairs of backtest files
    print("Prepare the backtest files for the first 10 pairs of coins...")
    coint_pairs_df = pd.read_csv(cointegrated_pairs_file_name)
    with open(prices_json_file_name) as json_file:
        price_data = json.load(json_file)
    for index, row in coint_pairs_df.iterrows():
        if index < number_of_backtest_pair:
            print(f"Creating backtest data for {row['sym_1']}, {row['sym_2']}...")
            if len(price_data) > 0:
                backtest_pair = row['sym_1'] + "_" + row['sym_2']
                analyse_pair(row['sym_1'], row['sym_2'], price_data, format(index+1)+"_"+backtest_pair)


    """
    # step 4 - plot trends and save for back-testing
    print("Plotting trends...")
    symbol_1 = "DOGEUSDT"
    symbol_2 = "GSTUSDT"
    with open(prices_json_file_name) as json_file:
        price_data = json.load(json_file)
        if len(price_data) > 0:
            plot_trends(symbol_1, symbol_2, price_data)
    """

    print("Done.")
