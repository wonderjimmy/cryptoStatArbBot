from config_execution_api import session_public


def get_order_book(ticker):
    data = session_public.orderbook(symbol=ticker)
    if data["ret_msg"] == "OK":
        orderbook = data["result"]
        return orderbook
    else:
        return None
