from Config.constant import SIGNAL_SIDE_POSITIVE, KILL_SWITCH_CLOSE_ORDER_POSITION, SIGNAL_SIDE_NEGATIVE
from func_calculations import get_trade_details
from func_price_calls import get_latest_klines
from func_stat import calculate_metrics
from func_order_book import get_order_book


# get latest zcore
def get_latest_zscore(ticker_1, ticker_2):
    # Get latest asset orderbook prices and add dummy price for latest
    # ws_public.orderbook_25_stream(handle_orderbook1, subs_public[0])

    # get orderbook and the mid-price by studying the order queue
    orderbook_1 = get_order_book(ticker_1)
    if orderbook_1:
        mid_price_1, _, _, = get_trade_details(orderbook_1)

    orderbook_2 = get_order_book(ticker_2)
    if orderbook_2:
        mid_price_2, _, _, = get_trade_details(orderbook_2)

    # Get latest price history
    series_1, series_2 = get_latest_klines(ticker_1, ticker_2)

    # Get z_score and confirm if hot
    if len(series_1) > 0 and len(series_2) > 0:

        # Replace last kline price with latest orderbook mid price
        series_1 = series_1[:-1]
        series_2 = series_2[:-1]
        series_1.append(mid_price_1)
        series_2.append(mid_price_2)

        # Get latest zscore
        _, zscore_list = calculate_metrics(series_1, series_2)
        zscore = zscore_list[-1]

        # Return output
        return zscore

    # Return output if not true
    return


def is_reversal_happened(ticker_1, ticker_2, signal_side):
    # get and save the latest zscore
    zscore = get_latest_zscore(ticker_1, ticker_2)

    # close positions
    if (signal_side == SIGNAL_SIDE_POSITIVE and zscore < 0) or (signal_side == SIGNAL_SIDE_NEGATIVE and zscore >= 0):
        return True
    else:
        return False


# Check is zscore suddenly changed
def is_zscore_sign_changed(zscore_old, zscore_new):

    if zscore_old > 0 and zscore_new > 0:
        return False
    if zscore_old < 0 and zscore_new < 0:
        return False
    if zscore_old == 0 and zscore_new == 0:
        return False

    return True
