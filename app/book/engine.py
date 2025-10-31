from collections import OrderedDict, defaultdict
from dataclasses import dataclass
from typing import Dict, List, Tuple

@dataclass
class Order:
    order_id: int
    side: str
    price: float
    size: float
    ts: float

# class Order:
#     def __init__(self, order_id, side, price, size, ts):
#         self.order_id = order_id
#         self.side = side
#         self.price = price
#         self.size = size
#         self.ts = ts

class PriceLevel:
    """Defines a class that manages all orders at a single price"""
    def __init__(self) -> None: 
        # OrderedDict works similar to a queue -> FIFO.
        # It keeps the the oldest order first, the newest last.
        # In markets, time priority matters - earlier orders\ 
        # get filled first if multiple exist at the same time.   
        self.orders = OrderedDict()

    def add(self, o: Order) -> None:
        # Adds a new order (o) to this price level, 
        # using its unique order_id as its key 
        self.orders[o.order_id] = o

    def remove(self, order_id: int) -> None: 
        # Removes an order (when canceled or filled)
        # In the event where the key doesn't exist,
        # it does nothing instead of raising an error.
        self.orders.pop(order_id, None)

    def best_qty(self) -> float: 
        # Sum up all order sizes currently in self.orders
        return sum(o.size for o in self.orders.values())
    
class OrderBook:
    """OrderBook (main engine) manages both sides of the book and applies updates"""
    def __init__(self) -> None:
        self.orders = {} # global lookup: order_id -> Order
        self.bids = defaultdict(PriceLevel)
        self.asks = defaultdict(PriceLevel)

    # pick which side of the book to update
    def _side_map(self, side: str):
        # return self.bids if side.upper().startswith("B") else self.asks

        # Handle non-string sides safely
        if not isinstance(side, str):
            # fallback — assume buy side if missing or invalid
            return self.bids
        side_upper = side.upper()
        if side_upper.startswith("B"):
            return self.bids
        return self.asks


    # --- Event Handlers ---
    def on_add(self, order_id: int, side: str, price: float, size: float,
                ts: float) -> None:
        """Add a brand-new order - like a bid or ask appearing in the market"""
        if order_id in self.orders:  # check the keys
            self.on_cancel(order_id) # clean duplicates
        o = Order(order_id, side, price, size, ts) # instantiate
        # print(o) # outputs: (order_id=12345, side='B', price=100.5, size=10, ts=...)
        self.orders[order_id] = o # append to dict
        self._side_map(size)[price].add(o) #

    def on_modify(self, order_id: int, new_price: float, new_size: float, 
                  ts: float) -> None:
        """If a resting order changes its size or price, move it to the
          next level (if needed) and update the size.
          This keeps price-time priority intact."""
        o = self.orders.get(order_id) # output: dict value
        if not o: # unknown -> ignore
            return
        # Price change -> move across levels (keep time or not per venue;\
        # we keep original)
        if new_price != o.price:
            self._side_map(o.side)[o.price].remove(order_id)
            o.price = new_price
            self._side_map(o.side)[o.price].add(o)
        # size update
        o.size = new_size
        o.ts = ts

    def on_cancel(self, order_id: int) -> None:
        """Deletes an order entirely - used for cancel or full trade fills"""
        o = self.orders.pop(order_id, None)
        if not o:
            return
        self._side_map(o.side)[o.price].remove(order_id)

    def on_trade(self, order_id: int, executed: float, ts: float) -> None:
        # Removes an orders remaining quantity when part/all of it trades.
        # Removes it if size hits zero 
        o = self.orders.get(order_id)
        if not o:
            return
        o.size -= executed
        o.ts = ts
        if o.size <= 0:
            self.on_cancel(order_id)

    def on_fill(self, order_id: int, executed: float, ts: float) -> None:
        self.on_trade(order_id, executed, ts)

    def on_clear(self) -> None:
        self.orders.clear()
        self.bids.clear()
        self.asks.clear()

    # --- Snapshots (top N aggregated) ---
    def top_levels(self, depth: int = 10):
        bids = sorted(self.bids.items(), key=lambda kv: kv[0], reverse=True)
        asks = sorted(self.asks.items(), key=lambda kv: kv[0])
        # agg_bids = [(p, lvl.best_qty()) for p, lvl in bids[:depth] if lvl.best_qty() > 0]
        # agg_asks = [(p, lvl.best_qty()) for p, lvl in asks[:depth] if lvl.best_qty() > 0]
        # return agg_bids, agg_asks

        # Ensure you only include pairs with valid data
        def safe_agg(levels):
            agg = []
            for p, lvl in levels[:depth]:
                qty = lvl.best_qty()
                if qty and qty > 0:
                    agg.append([float(p), float(qty)])  # ensure 2-element lists
            return agg

        return safe_agg(bids), safe_agg(asks)

    def to_json_obj(self, instrument, ts, depth=10):
        bids, asks = self.top_levels(depth)
        return {"instrument": instrument, "ts": ts, "bids": bids, "asks": asks}        