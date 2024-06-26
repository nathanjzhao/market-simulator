import json
import logging
import heapq
from collections import defaultdict

from backend.utils.logging import log_variables
from backend.utils.schema import DecimalEncoder, Leaderboard, User
from backend.utils.db import get_db, get_or_create


logging.basicConfig(level=logging.INFO)
db = next(get_db())

# initialize logger
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
log = logging.getLogger(__name__)

class OrderBook:
    def __init__(self):
        self.bid_queues = defaultdict(list) # highest price is best
        self.ask_queues = defaultdict(list) # lowest price is best
        self.user_order_counts = defaultdict(int) # count of orders per user
        self.max_orders_per_user = 10

    def push(self, request):
        user_id = request['user_id']
        symbol = request['symbol']
        request_type = request['dir']

        # Check if the user has reached their limit
        if self.user_order_counts[user_id] >= self.max_orders_per_user:
            log.info(f"User with id {user_id} has reached the maximum number of orders ({self.max_orders_per_user}).")
            return None

        # Add the request to the appropriate queue
        if request_type == 'BUY':
            price_priority = request['price'] 
            time_priority = request['timestamp']  
            heapq.heappush(self.bid_queues[symbol], (price_priority, time_priority, request))
        elif request_type == 'SELL':
            price_priority = request['price']
            time_priority = request['timestamp'] 
            heapq.heappush(self.ask_queues[symbol], (price_priority, time_priority, request))

        # Increment the user's order count
        self.user_order_counts[user_id] += 1

        return self.fulfill(symbol)

    def peek(self, symbol, request_type):
        # Get the highest priority request from the appropriate queue without removing it
        if request_type == 'BUY' and self.bid_queues[symbol]:
            _, _, request = heapq.nlargest(1, self.bid_queues[symbol])[0]
            return request
        elif request_type == 'SELL' and self.ask_queues[symbol]:
            _, _, request = heapq.nsmallest(1, self.ask_queues[symbol])[0]
            return request
        else:
            return None
        
    def fulfill(self, symbol):
            matches = []
            match = self.match(symbol)
            while match is not None:
                print(match)
                matches.append(match)
                match = self.match(symbol)
            return matches

    def match(self, symbol):
        # Check if there are both bids and asks for the symbol
        while self.bid_queues[symbol] and self.ask_queues[symbol]:
            # Get the highest bid and the lowest ask
            bid_priority, _, bid = heapq.nlargest(1, self.bid_queues[symbol])[0]
            ask_priority, _, ask = heapq.nsmallest(1, self.ask_queues[symbol])[0]

            log.info(f"bid_priority: {bid_priority}, ask_priority: {ask_priority}")

            # If the highest bid is greater than or equal to the lowest ask, they match
            if bid_priority >= ask_priority:
                # Determine the number of shares that can be exchanged
                shares = min(bid['shares'], ask['shares'])

                # Update the number of shares in the bid and ask
                bid['shares'] -= shares
                ask['shares'] -= shares

                # If a bid or ask has been completely fulfilled, remove it from the queue and decrease the user's order count
                if bid['shares'] == 0:
                    heapq.heappop(self.bid_queues[symbol])
                    self.user_order_counts[bid['user_id']] -= 1
                if ask['shares'] == 0:
                    heapq.heappop(self.ask_queues[symbol])
                    self.user_order_counts[ask['user_id']] -= 1

                # Return the matching bid, ask, and the number of shares exchanged
                return bid, ask, shares
            else:
                return None
    
    def cancel_order(self, symbol, user_id, order_id):
        # Check both the bid and ask queues for the order
        for queue in [self.bid_queues[symbol], self.ask_queues[symbol]]:
            for i in range(len(queue)):
                _, _, order = queue[i]
                if order['order_id'] == order_id and order['user_id'] == user_id:
                    # Remove the order from the queue
                    del queue[i]

                    # Decrease the user's order count
                    self.user_order_counts[user_id] -= 1
                    return True
        return False
    
    def get_order(self, symbol, user_id, order_id):
        # Check both the bid and ask queues for the order
        for queue in [self.bid_queues[symbol], self.ask_queues[symbol]]:
            for i in range(len(queue)):
                _, _, order = queue[i]
                if order['order_id'] == order_id and order['user_id'] == user_id:
                    return order, True
        return None, False
        
    async def process_fulfillments(self, fulfillments, kafka_producer, KAFKA_TOPIC):
        for bid, ask, shares in fulfillments:

            if bid['user'] == ask['user']:
                bid['op'], bid['shares'] = 'Cancelled', shares
                ask['op'], ask['shares'] = 'Cancelled', shares

                bid_request_json = json.dumps(bid, cls=DecimalEncoder).encode('utf-8')
                ask_request_json = json.dumps(ask, cls=DecimalEncoder).encode('utf-8')

                try:
                    bid_request_json = json.dumps(bid, cls=DecimalEncoder).encode('utf-8')
                    ask_request_json = json.dumps(ask, cls=DecimalEncoder).encode('utf-8')
                except Exception as e:
                    log_variables(error=e)

                try:
                    await kafka_producer.send_and_wait(KAFKA_TOPIC, bid_request_json)
                    await kafka_producer.send_and_wait(KAFKA_TOPIC, ask_request_json)
                except Exception as e:
                    log_variables(error=e)
        
            # Get or create the user from the leaderboard for the bid
            bid_user, created = get_or_create(db, Leaderboard, defaults={'username' : bid['user'], 'user_id': bid['user_id']}, username=bid['user'])
            if created:
                db.add(bid_user)
                db.commit()

            # Get or create the user from the leaderboard for the ask
            ask_user, created = get_or_create(db, Leaderboard, defaults={'username' : ask['user'], 'user_id': ask['user_id']}, username=ask['user'])
            if created:
                db.add(ask_user)
                db.commit()

            # Update scores
            bid_user.score -= float(shares * bid['price'])
            ask_user.score += float(shares * ask['price'])

            bid_user.symbols[bid['symbol']] += shares
            ask_user.symbols[ask['symbol']] -= shares
            db.is_modified(bid_user, include_collections=True)
            db.is_modified(ask_user, include_collections=True)

        # Commit the changes to the database
        db.commit()
    
    def to_dict(self):
        result = {}
        for symbol in set(list(self.bid_queues.keys()) + list(self.ask_queues.keys())):
            result[symbol] = {
                "Bids": [{"Price": price, "Shares": bid['shares'], "Timestamp": timestamp} for price, timestamp, bid in sorted(self.bid_queues[symbol], reverse=True)],
                "Asks": [{"Price": price, "Shares": ask['shares'], "Timestamp": timestamp} for price, timestamp, ask in sorted(self.ask_queues[symbol])],
            }
        return result

    def to_json(self):
        return json.dumps(self.to_dict(), cls=DecimalEncoder, default=str)
    
    def __str__(self):
        result = []
        for symbol in set(list(self.bid_queues.keys()) + list(self.ask_queues.keys())):
            result.append(f"Symbol: {symbol}")
            result.append("Bids:")
            for price, timestamp, bid in sorted(self.bid_queues[symbol], reverse=True):
                result.append(f"  Price: {price}, Shares: {bid['shares']}, Timestamp: {timestamp}")
            result.append("Asks:")
            for price, timestamp, ask in sorted(self.ask_queues[symbol]):
                result.append(f"  Price: {price}, Shares: {ask['shares']}, Timestamp: {timestamp}")
        return "\n".join(result)
    
