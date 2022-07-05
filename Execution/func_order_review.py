from Execution.config_execution_api import is_debug
from func_position_calls import query_existing_order, get_open_position
from Config.constant import *


# check order items
def check_order(ticker, order_id, remaining_capital, direction=ORDER_DIRECTION_LONG):

    order_price, order_quantity, order_status = query_existing_order(ticker, order_id)

    # Get open positions
    position_price, position_quantity, position_value = get_open_position(ticker, direction)

    # Determine action - trade complete - stop placing orders
    # If position value > remaining capital, no more trade should be made

    # determine the action - position filled
    if order_status == "Filled":
        return "Position Filled"

    # determine the action - order active - do nothing
    active_items = ["Created", "New"]
    if order_status in active_items:
        return "Order Active"

    # determine the action - partially filled order - do nothing
    if order_status == "PartiallyFilled":
        return "Partial Fill"

    # determine the action - order failed - try place order again
    cancel_items = ["Cancelled", "Rejected", "PendingCancel"]
    if order_status in cancel_items:
        return "Try Again"
