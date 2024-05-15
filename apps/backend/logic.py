import heapq
from collections import defaultdict

class SymbolQueues:
    def __init__(self):
        self.bid_queues = defaultdict(list)
        self.ask_queues = defaultdict(list)

    def push(self, symbol, request, request_type):
        # Add the request to the appropriate queue
        print(type(request['price']))
        if request_type == 'bid':
            priority = request['price']  # Use positive price to get lowest (latest) first
            heapq.heappush(self.bid_queues[symbol], (priority, request))
        elif request_type == 'ask':
            priority = -request['price']  # Use negative price to get highest (latest) first
            heapq.heappush(self.ask_queues[symbol], (priority, request))

    def pop(self, symbol, request_type):
        # Get the next request from the appropriate queue
        if request_type == 'bid' and self.bid_queues[symbol]:
            priority, request = heapq.heappop(self.bid_queues[symbol])
            return request
        elif request_type == 'ask' and self.ask_queues[symbol]:
            priority, request = heapq.heappop(self.ask_queues[symbol])
            return request
        else:
            return None

    def peek(self, symbol, request_type):
        # Get the highest priority request from the appropriate queue without removing it
        if request_type == 'bid' and self.bid_queues[symbol]:
            priority, request = heapq.nlargest(1, self.bid_queues[symbol])[0]
            return request
        elif request_type == 'ask' and self.ask_queues[symbol]:
            priority, request = heapq.nlargest(1, self.ask_queues[symbol])[0]
            return request
        else:
            return None
        
    def match(self, symbol):
        # Check if there are both bids and asks for the symbol
        while self.bid_queues[symbol] and self.ask_queues[symbol]:
            # Get the highest bid and the lowest ask
            bid_priority, bid = heapq.nlargest(1, self.bid_queues[symbol])[0]
            ask_priority, ask = heapq.nsmallest(1, self.ask_queues[symbol])[0]

            # If the highest bid is greater than or equal to the lowest ask, they match
            if bid_priority >= -ask_priority:
                # Determine the number of shares that can be exchanged
                shares = min(bid['shares'], ask['shares'])

                # Update the number of shares in the bid and ask
                bid['shares'] -= shares
                ask['shares'] -= shares

                # If a bid or ask has been completely fulfilled, remove it from the queue
                if bid['shares'] == 0:
                    heapq.heappop(self.bid_queues[symbol])
                if ask['shares'] == 0:
                    heapq.heappop(self.ask_queues[symbol])

                # Return the matching bid, ask, and the number of shares exchanged
                return bid, ask, shares

        # If there's no match, return None
        return None