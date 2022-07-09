from config_strategy_api import session

# get symbols that are tradable


def get_tradable_symbols():
    sym_list = []
    symbols = session.query_symbol()
    if "ret_msg" in symbols.keys():
        if symbols["ret_msg"] == "OK":
            symbols = symbols["result"]
            for symbol in symbols:
                #if symbol["quote_currency"] == "USDT" and float(symbol["maker_fee"]) < 0 and symbol["status"] == "Trading":
                if symbol["quote_currency"] == "USDT" and symbol["status"] == "Trading":
                    sym_list.append(symbol)
    return sym_list
