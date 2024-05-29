import json
import os
import uuid
import time
import asyncio
from backend.utils.schema import DecimalEncoder
from dotenv import load_dotenv

load_dotenv()

SYMBOLS = os.getenv('SYMBOLS').split(',')

def buy(orderbook, user, symbol, amount, price, producer, KAFKA_TOPIC):
    """
    Creates a buy order.

    Args:
        symbol (str): The symbol of the stock to buy.
        amount (int): The number of shares to buy.
        price (float): The price per share.

    Returns:
        str: The ID of the created order.
    """
    order_id = str(uuid.uuid4())
    request_dict = {
        'symbol': symbol,
        'dir': 'SELL',
        'price': str(price),
        'shares': amount,
        'op': 'Created',
        'user_id': user.id,
        'order_id': order_id,
        'timestamp': int(time.time()),
        'user': user.username,
    }

    request_json = json.dumps(request_dict, cls=DecimalEncoder).encode('utf-8')
    asyncio.create_task(producer.send_and_wait(KAFKA_TOPIC, request_json))

    fulfillments = orderbook.push(request_dict)
    asyncio.create_task(orderbook.process_fulfillments(fulfillments, producer, KAFKA_TOPIC))

    return order_id

def sell(orderbook, user, symbol, amount, price, producer, KAFKA_TOPIC):
    """
    Creates a sell order.

    Args:
        symbol (str): The symbol of the stock to sell.
        amount (int): The number of shares to sell.
        price (float): The price per share.

    Returns:
        str: The ID of the created order.
    """
     
    order_id = str(uuid.uuid4())
    request_dict = {
        'symbol': symbol,
        'dir': 'SELL',
        'price': str(price),
        'shares': amount,
        'op': 'Created',
        'user_id': user.id,
        'order_id': order_id,
        'timestamp': int(time.time()),
        'user': user.username,
    }
    request_json = json.dumps(request_dict, cls=DecimalEncoder).encode('utf-8')
    asyncio.create_task(producer.send_and_wait(KAFKA_TOPIC, request_json))

    fulfillments = orderbook.push(request_dict)
    asyncio.create_task(orderbook.process_fulfillments(fulfillments, producer, KAFKA_TOPIC))

    return order_id
    

# return True if order cancelled
def cancel_order(orderbook, user, order_id):
    """
    Cancels an order.

    Args:
        order_id (str): The ID of the order to cancel.

    Returns:
        bool: True if the order was cancelled, False otherwise.
    """
    return orderbook.cancel_order(user.id, order_id)

def get_top(orderbook, symbol, direction):
    """
    Gets the top order for a given symbol and buy/sell direction.

    Args:
        symbol (str): The symbol of the stock.
        direction (str): The direction of the order ('BUY' or 'SELL').

    Returns:
        Order: The top order.
    """
    return orderbook.peek(symbol, direction.upper())

def get_order(orderbook, user, order_id):
    """
    Gets an order according to an order_id

    Args:
        order_id (str): The ID of the order to get.

    Returns:
        Order: The order if found
        bool: True if the order was found, False otherwise.
    """
    return orderbook.get_order(user.id, order_id)

def get_orders(orderbook, user):
    """
    Gets all orders for a user.

    Returns:
        dict: A dictionary representation of all orders.
    """
    return orderbook.to_dict()

def get_symbols():
    """
    Gets all available symbols.

    Returns:
        list: A list of all available symbols.
    """
    return SYMBOLS