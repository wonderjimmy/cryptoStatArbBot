from config_strategy_api import prices_json_file_name
from func_price_klines import get_price_klines
import json
# store price history for all available pairs
def store_price_history(symbols):

    # get prices and store in dataframe
    counts = 0
    price_history_dict = {}
    for sym in symbols:
        symbol_name = sym["name"]
        price_history = get_price_klines(symbol_name)
        if len(price_history) > 0:
            price_history_dict[symbol_name] = price_history
            counts += 1
            print(f"{counts} items stored")
        else:
            print(f"{counts} items not stored")

    # output prices to json
    if len(price_history_dict) > 0:
        with open(prices_json_file_name, "w") as fp:
            json.dump(price_history_dict, fp, indent=4)
        print("Prices saved successfully.")

    return


