from config_execution_api import ws_public_url
from config_execution_api import ticker_1
from config_execution_api import ticker_2

from pybit import usdt_perpetual
from time import sleep

'''
NOT USED ANYMORE
'''


# public websocket subscription
subs_public = [f"{ticker_1}", f"{ticker_2}"]

# public websocket subscription
ws_public = usdt_perpetual.WebSocket(
    test=True
)


def handle_orderbook(message):
    # print(message)
    orderbook_data = message["data"]


# Now, we can subscribe to the orderbook stream and pass our arguments:
# our function and our selected symbol.
# To subscribe to multiple symbols, pass a list: ["BTCUSD", "ETHUSD"]
# To subscribe to all symbols, pass "*".
ws_public.orderbook_25_stream(handle_orderbook, subs_public)

"""
while True:
    # This while loop is required for the program to run. You may execute
    # additional code for your trading logic here.
    sleep(1)
"""
