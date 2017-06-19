"""
Market Making Sim Order Book

This order book has two functions:

1) Randomly generate new orders and trades
2) Handle orders submitted by the strategy under test

Each order object has fields:

type_id : type of asset
order_id : unique order ID
issue_time : simulation time when order was issued
buy : true for buy orders, false otherwise
duration : duration in days
expire_time : simulation time when this order will expire
price : current order price
min_volume : minimum transaction volume for order
volume : current volume for order

"""
import pandas as pd
import numpy.random
from evekit.sim import create_sample_generator, create_boolean_sample_generator


class TradeRecorder:
    def __init__(self):
        self.trades = []
        self.actions = []

    def record_trade(self, trade):
        self.trades.append(trade)

    def order_action(self, record):
        self.actions.append(record)


class MMSimOrderBook:

    def __init__(self, ref_price, ref_spread, type_id, inferred_trades, inferred_orders, oms, seed):
        self.ref_price = ref_price
        self.ref_spread = ref_spread
        self.type_id = type_id
        self.bid = []
        self.ask = []
        self.snapshot = None
        self.snapshot_time = 0
        self.next_order_id = 1
        self.oms = oms
        self.seed = seed
        self.rand_gen = numpy.random.RandomState(seed)
        self._setup_trade_generator(inferred_trades)
        self._setup_new_order_generator(inferred_orders)
        self._setup_change_order_generator(inferred_orders)
        self._setup_cancel_order_generator(inferred_orders)

    @staticmethod
    def _trade_generator(side_gen, buy_vol_gen, sell_vol_gen, arrival_time_gen):
        def get_next_trade():
            next_side = side_gen()
            next_volume = max(buy_vol_gen() if next_side else sell_vol_gen(), 1)
            next_arrival = max(arrival_time_gen(), 1)
            return dict(arrival=next_arrival, buy=next_side, volume=next_volume)

        return get_next_trade

    @staticmethod
    def _new_order_generator(side_gen, duration_gen, arrival_time_gen, min_vol_gen, vol_gen, tob_gen):
        def get_next_new_order():
            next_side = side_gen()
            next_duration = duration_gen()
            next_arrival = max(arrival_time_gen(), 1)
            next_min_vol = max(min_vol_gen(), 1)
            next_vol = max(vol_gen(), 1)
            next_tob = tob_gen()
            return dict(arrival=next_arrival, buy=next_side, duration=next_duration, min_volume=next_min_vol,
                        volume=next_vol, tob=next_tob)

        return get_next_new_order

    @staticmethod
    def _change_cancel_order_generator(side_gen, arrival_time_gen):
        def get_next_order():
            next_side = side_gen()
            next_arrival = max(arrival_time_gen(), 1)
            return dict(arrival=next_arrival, buy=next_side)

        return get_next_order

    def _setup_trade_generator(self, inferred_trades):
        buy_trades = [x for x in inferred_trades if x['buy']]
        sell_trades = [x for x in inferred_trades if not x['buy']]
        # Create volume generators by side
        buy_vol_gen = create_sample_generator([x['volume'] for x in buy_trades], 1000, self.seed)
        sell_vol_gen = create_sample_generator([x['volume'] for x in sell_trades], 1000, self.seed)
        # Create inter arrival time generator
        trade_inter_arrival = pd.Series([x['time'] for x in inferred_trades]).diff()[1:].apply(lambda x: x.seconds)
        trade_skewer = numpy.random.RandomState(self.seed)
        trade_inter_arrival = trade_inter_arrival.apply(lambda x: x + int(trade_skewer.rand() * 300))
        trade_arrival_gen = create_sample_generator(list(trade_inter_arrival), 10000, self.seed)
        # Create trade side generator
        trade_side_gen = create_boolean_sample_generator(len(buy_trades), len(sell_trades), self.seed)
        # Finally, create trade generator
        self.trade_generator = MMSimOrderBook._trade_generator(trade_side_gen, buy_vol_gen, sell_vol_gen,
                                                               trade_arrival_gen)

    def _setup_new_order_generator(self, inferred_orders):
        new_orders = [x for x in inferred_orders if x['action'] == 'new']
        # Create order side generator
        buy_orders = [x for x in new_orders if x['buy']]
        sell_orders = [x for x in new_orders if not x['buy']]
        new_order_side = create_boolean_sample_generator(len(buy_orders), len(sell_orders), self.seed)
        # Create duration generator.  Note that we need ot constrain values to a specific set.  We build
        # the generator from an index into the allowable durations, then reverse the mapping when we
        # generate sample values.
        allowed_durations = [1, 3, 7, 14, 30, 90]
        durations = [allowed_durations.index(x['duration']) for x in new_orders if x['duration'] > 0]
        duration_sample_gen = create_sample_generator(durations, 1000, self.seed)

        def sample_from_range():
            return allowed_durations[duration_sample_gen()]
        new_order_duration = sample_from_range
        # Create inter arrival time generator
        new_order_inter_arrival_samples = pd.Series([x['time'] for x in new_orders]).diff()[1:]\
                                            .apply(lambda x: x.seconds)
        new_order_skewer = numpy.random.RandomState(self.seed)
        new_order_inter_arrival_samples = new_order_inter_arrival_samples.apply(lambda x: x + int(new_order_skewer.rand() * 300))
        new_order_inter_arrival = create_sample_generator(list(new_order_inter_arrival_samples), 10000, self.seed)
        # Create min volume generator
        new_order_min_volume = create_sample_generator([x['min_volume'] for x in new_orders], 1000, self.seed)
        # Create volume generator
        new_order_volume = create_sample_generator([x['volume'] for x in new_orders], 1000, self.seed)
        # Create "top of book" selector
        new_order_tob = create_boolean_sample_generator(len([x for x in new_orders if x['tob']]),
                                                        len([x for x in new_orders if not x['tob']]),
                                                        self.seed)
        # Finally, create the new order generator
        self.new_order_generator = MMSimOrderBook._new_order_generator(new_order_side, new_order_duration,
                                                                       new_order_inter_arrival, new_order_min_volume,
                                                                       new_order_volume, new_order_tob)

    def _setup_change_order_generator(self, inferred_orders):
        change_orders = [x for x in inferred_orders if x['action'] == 'change']
        # Create order side generator
        buy_orders = [x for x in change_orders if x['buy']]
        sell_orders = [x for x in change_orders if not x['buy']]
        change_order_side = create_boolean_sample_generator(len(buy_orders), len(sell_orders), self.seed)
        # Create inter arrival time generator
        change_order_inter_arrival_samples = pd.Series([x['time'] for x in change_orders]).diff()[1:]\
                                               .apply(lambda x: x.seconds)
        change_order_skewer = numpy.random.RandomState(self.seed)
        change_order_inter_arrival_samples = change_order_inter_arrival_samples.apply(lambda x: x + int(change_order_skewer.rand() * 300))
        change_order_inter_arrival = create_sample_generator(list(change_order_inter_arrival_samples), 10000, self.seed)
        self.change_order_generator = MMSimOrderBook._change_cancel_order_generator(change_order_side,
                                                                                    change_order_inter_arrival)

    def _setup_cancel_order_generator(self, inferred_orders):
        cancel_orders = [x for x in inferred_orders if x['action'] == 'cancel']
        # Create order side generator
        buy_orders = [x for x in cancel_orders if x['buy']]
        sell_orders = [x for x in cancel_orders if not x['buy']]
        cancel_order_side = create_boolean_sample_generator(len(buy_orders), len(sell_orders), self.seed)
        # Create inter arrival time generator
        cancel_order_inter_arrival_samples = pd.Series([x['time'] for x in cancel_orders]).diff()[1:]\
                                               .apply(lambda x: x.seconds)
        cancel_order_skewer = numpy.random.RandomState(self.seed)
        cancel_order_inter_arrival_samples = cancel_order_inter_arrival_samples.apply(lambda x: x + int(cancel_order_skewer.rand() * 300))
        cancel_order_inter_arrival = create_sample_generator(list(cancel_order_inter_arrival_samples), 10000, self.seed)
        self.cancel_order_generator = MMSimOrderBook._change_cancel_order_generator(cancel_order_side,
                                                                                    cancel_order_inter_arrival)

    def _make_snapshot(self, env):
        all_orders = self.bid + self.ask
        self.snapshot = pd.DataFrame(all_orders, index=range(len(all_orders)))
        self.snapshot_time = env.now

    def dataframe(self):
        """
        Produce the current order book as a data frame
        :return: the current book as a dataframe
        """
        return self.snapshot

    @staticmethod
    def _create_next_book_event(generator, env):
        next_event_value = generator()
        return env.timeout(next_event_value['arrival'], value=next_event_value)

    def _match_orders(self, env, trade_recorder=None):
        """
        Look for matchable orders and record any trades that result.
        Orders are matchable as long as the spread is crossed.  We service the lowest
        ask first.
        """
        def clean_side(side):
            """
            Remove trade orders from a side.
            :param side: a side containing orders
            :return: the tuple r, k with r giving the number of orders removed, and k an array of
            the remaining orders.
            """
            kept = [x for x in side if not x['trade_order']]
            return len(kept), kept

        if trade_recorder is None:
            trade_recorder = self.oms

        while len(self.ask) > 0 and len(self.bid) > 0 and self.ask[0]['price'] <= self.bid[0]['price']:
            # For simplicity, we ignore min_volume for now
            top_bid = self.bid[0]
            top_ask = self.ask[0]
            max_trade_amount = min(top_bid['volume'], top_ask['volume'])
            trade_price = max(top_bid['price'], top_ask['price'])
            trigger = None
            if top_bid['trade_order']:
                trigger = 'buy_trade'
            elif top_ask['trade_order']:
                trigger = 'sell_trade'
            trade_record = dict(time=env.now, type_id=self.type_id, volume=max_trade_amount,
                                price=trade_price, bid_id=top_bid['order_id'], ask_id=top_ask['order_id'],
                                bid_origin=top_bid['origin'], ask_origin=top_ask['origin'],
                                trigger=trigger)
            trade_recorder.record_trade(trade_record)
            top_bid['volume'] -= max_trade_amount
            top_ask['volume'] -= max_trade_amount
            if top_bid['volume'] == 0:
                order_record = dict(time=env.now, action='filled', order_id=top_bid['order_id'], bid=True,
                                    type_id=self.type_id)
                self.bid.pop(0)
                trade_recorder.order_action(order_record)
            if top_ask['volume'] == 0:
                order_record = dict(time=env.now, action='filled', order_id=top_ask['order_id'], bid=False,
                                    type_id=self.type_id)
                self.ask.pop(0)
                trade_recorder.order_action(order_record)
        # Upon matching completion, any trade orders must be removed (they have duration 'immediate')
        r, k = clean_side(self.bid)
        if r > 0:
            self.bid = k
        r, k = clean_side(self.ask)
        if r > 0:
            self.ask = k

    def _handle_new_order(self, env, order_event):
        """
        Handle new simulated order.  If "tob" is set, then the order is always placed at top of book
        on the appropriate side with a price 0.01 ISK better than the current top of book.  Otherwise,
        we exponentially distribute the new order on the appropriate side.  The exponential distribution
        will favor placing the order near the top of the book.  The price of the new order is set to be
        0.01 ISK better than the order immediately behind the new order.  If this is the first order for
        a side, then the price is set at an offset from the reference price.
        
        :param order_event: a new order event as created by the "new order generator" (see above).  A new order
        is a dictionary of the form: {'arrival': 187, 'buy': False, 'duration': 30, 'min_volume': 1, 
                                      'volume': 4866620, 'tob': True} 
        """
        bid = order_event['buy']
        side = self.bid if bid else self.ask
        expire_time = env.now + (order_event['duration'] * 24 * 60 * 60)
        # Formulate order price.  Initially, we'll generate a random offset from the reference price
        # appropriate for the side.
        price = self.ref_price + (-1 if bid else 1) * self.ref_spread * self.rand_gen.uniform()
        price = int(price * 100) / 100.0
        # If this is the first order on this side, then place it and we're done
        # Otherwise, place the order as appropriate.
        if len(side) == 0:
            # First order on this side, place at the top and we're done
            new_order = dict(type_id=self.type_id, order_id=self.next_order_id, issue_time=env.now,
                             buy=bid, duration=order_event['duration'], expire_time=expire_time,
                             price=price, min_volume=order_event['min_volume'], volume=order_event['volume'],
                             origin='simulated', trade_order=False)
            self.next_order_id += 1
            order_record = dict(time=env.now, action='created')
            order_record.update(new_order)
            self.oms.order_action(order_record)
            side.append(new_order)
        else:
            # Side already has orders.  If "tob" is True, then this is the new top of book.
            # Otherwise, place randomly within the current side biased towards placement at the top of book.
            if order_event['tob']:
                price = side[0]['price'] + (1 if bid else -1) * 0.01
                new_order = dict(type_id=self.type_id, order_id=self.next_order_id, issue_time=env.now,
                                 buy=bid, duration=order_event['duration'], expire_time=expire_time,
                                 price=price, min_volume=order_event['min_volume'], volume=order_event['volume'],
                                 origin='simulated', trade_order=False)
                self.next_order_id += 1
                order_record = dict(time=env.now, action='created')
                order_record.update(new_order)
                self.oms.order_action(order_record)
                side.insert(0, new_order)
            else:
                # Find position of order we'll be placed after
                position = self.rand_gen.geometric(0.5)
                position = min(position, len(side))
                position -= 1
                price = side[position]['price'] + (-1 if bid else 1) * 0.01
                # Now create order and insert into appropriate position
                new_order = dict(type_id=self.type_id, order_id=self.next_order_id, issue_time=env.now,
                                 buy=bid, duration=order_event['duration'], expire_time=expire_time,
                                 price=price, min_volume=order_event['min_volume'], volume=order_event['volume'],
                                 origin='simulated', trade_order=False)
                self.next_order_id += 1
                order_record = dict(time=env.now, action='created')
                order_record.update(new_order)
                self.oms.order_action(order_record)
                while position < len(side) and ((bid and side[position]['price'] > price) or
                                                (not bid and side[position]['price'] < price)):
                    position += 1
                side.insert(position, new_order)

    def _handle_change_order(self, env, order_event):
        """
        Handle a change to a simulated order.  Change orders always moved the changed order to the top
        of the book on the appropriate side.  The order to change is selected randomly using an exponential
        distribution which therefore favors orders already near the top of the book.  The price of the changed
        order is set to 0.01 ISK better than the previous best offer.  If the selected order already has
        the best price, then this event is silently ignored.

        :param order_event: a change order event as created by the "change order generator" (see above).  A change 
        order is a dictionary of the form: {'arrival': 187, 'buy': False} 
        """
        bid = order_event['buy']
        side = self.bid if bid else self.ask
        if len(side) <= 1 or len([x for x in side if x['origin'] == 'simulated']) == 0:
            # No simulated orders to re-price, silently drop this event
            return
        # Determine which order to modify.  Note that we can only modify simulated orders.
        # We'll rotate position until we find a simulated order to reposition.
        position = self.rand_gen.geometric(0.5)
        position = min(position, len(side))
        position -= 1
        while side[position]['origin'] != 'simulated':
            position += 1
            position %= len(side)
        # Push the order to the top of the side
        target_order = side.pop(position)
        side.insert(0, target_order)
        # If the order already has the best price, then we're done.
        # Otherwise, reprice the order and re-set issue data and expire_time
        old_price = target_order['price']
        price = None
        if target_order['price'] != side[1]['price']:
            if bid and target_order['price'] < side[1]['price']:
                price = side[1]['price'] + 0.01
            elif not bid and target_order['price'] > side[1]['price']:
                price = side[1]['price'] - 0.01
        if price is not None:
            target_order['price'] = price
            target_order['issue_time'] = env.now
            target_order['expire_time'] = env.now + (target_order['duration'] * 24 * 60 * 60)
        order_record = dict(time=env.now, action='change', order_id=target_order['order_id'], old_price=old_price,
                            new_price=price, type_id=self.type_id)
        self.oms.order_action(order_record)

    def _handle_cancel_order(self, env, order_event):
        """
        Handle cancellation of a simulated order.  Cancelled orders are simply removed from the book.

        :param order_event: a cancel order event as created by the "cancel order generator" (see above).  A cancel
        order is a dictionary of the form: {'arrival': 187, 'buy': False} 
        """
        bid = order_event['buy']
        side = self.bid if bid else self.ask
        if len([x for x in side if x['origin'] == 'simulated']) == 0:
            # No simulated orders to cancel, silently drop this event
            return
        # Determine which order to cancel.  Note that we can only modify simulated orders.
        # We'll rotate position until we find a simulated order to reposition.
        position = len(side) - self.rand_gen.geometric(0.5)
        position = max(position, 0)
        while side[position]['origin'] != 'simulated':
            position += 1
            position %= len(side)
        # Remove the cancelled order
        removed = side.pop(position)
        order_record = dict(time=env.now, action='canceled', order_id=removed['order_id'], type_id=self.type_id)
        self.oms.order_action(order_record)

    def _handle_expire_order(self, env, order_id):
        """
        Handle order expiration.  If the order with the given ID no longer exists, then we silently
        ignore this event.  If the order still exists, then its expire time is compared with the 
        current time.  The order is cancelled if the current time is equal to or after the expire
        time.

        :param order_id: the ID of the order to expire. 
        :return: the expired order, or None if the given order_id was not found or not expired.
        """
        def remove_expired(side):
            for i in range(len(side)):
                order = side[i]
                if order['order_id'] == order_id:
                    if order['expire_time'] <= env.now:
                        return side.pop(i)
                    else:
                        return None
            return None
        result = remove_expired(self.bid)
        if result is not None:
            return result
        return remove_expired(self.ask)

    def _handle_trade(self, env, trade_event):
        """
        Handle simulated trade.  Trades are simulated as orders at a price which crosses the spread 
        on the appropriate side.  A trade with leftover volume is always discarded.  That is,
        unfilled trades are not left on the book as limit orders.

        :param trade_event: a new trade event as created by the "trade generator" (see above).  A new trade
        is a dictionary of the form: {'arrival': 187, 'buy': False, 'volume': 4866620} 
        """
        bid = trade_event['buy']
        side = self.bid if bid else self.ask
        trade_side = self.ask if bid else self.bid
        if len(trade_side) == 0:
            # No orders allow us to cross the spread, silently discard the trade.
            return
        # "Order" price is always the current best offer across the spread.
        price = trade_side[0]['price']
        # By construction, the trade is always the top of book
        new_order = dict(type_id=self.type_id, order_id=self.next_order_id, issue_time=env.now,
                         buy=bid, duration=1, expire_time=env.now, price=price, min_volume=1,
                         volume=trade_event['volume'], origin='simulated', trade_order=True)
        self.next_order_id += 1
        side.insert(0, new_order)

    def _next_book_expiry(self, env):
        """
        Return an event indicating when the next order will expire from the order book.
        
        :param env: simulation environment 
        :return: a Timeout event with value equal to the order ID of the next order which will
        expire.  The timeout will be set to five simulated minutes if there are currently no
        orders (and value will be None).
        """
        if len(self.bid) == 0 and len(self.ask) == 0:
            return env.timeout(5 * 60)
        min_expire = None
        min_order_id = None
        for x in self.bid + self.ask:
            if min_order_id is None or x['expire_time'] < min_expire:
                min_expire = x['expire_time']
                min_order_id = x['order_id']
        return env.timeout(min_expire - env.now, value=min_order_id)

    def warmup(self, env, count):
        for _ in range(count):
            next_order = self.new_order_generator()
            self._handle_new_order(env, next_order)

    def run(self, env):
        """
        Main event loop for order and trade arrival stream.  This routine performs two tasks:
        1. Generates a snapshot of the order book every five minutes to be provided to the strategy under test
        2. Awaits and processes the next random order or trade event.
        
        :param env: the simpy environment for this simulation.
        """
        next_snapshot = env.timeout(self.snapshot_time + 300 - env.now)
        next_trade = MMSimOrderBook._create_next_book_event(self.trade_generator, env)
        next_new_order = MMSimOrderBook._create_next_book_event(self.new_order_generator, env)
        next_change_order = MMSimOrderBook._create_next_book_event(self.change_order_generator, env)
        next_cancel_order = MMSimOrderBook._create_next_book_event(self.cancel_order_generator, env)
        next_expire = self._next_book_expiry(env)
        while True:
            result = yield next_snapshot | next_trade | next_new_order | next_change_order | \
                           next_cancel_order | next_expire
            if next_snapshot in result.keys():
                self._make_snapshot(env)
                next_snapshot = env.timeout(self.snapshot_time + 300 - env.now)
                self.oms.new_snapshot(env, self.type_id, self.dataframe())
            elif next_trade in result.keys():
                self._handle_trade(env, result[next_trade])
                self._match_orders(env)
                next_trade = MMSimOrderBook._create_next_book_event(self.trade_generator, env)
                next_expire = self._next_book_expiry(env)
            elif next_new_order in result.keys():
                self._handle_new_order(env, result[next_new_order])
                self._match_orders(env)
                next_new_order = MMSimOrderBook._create_next_book_event(self.new_order_generator, env)
                next_expire = self._next_book_expiry(env)
            elif next_change_order in result.keys():
                self._handle_change_order(env, result[next_change_order])
                self._match_orders(env)
                next_change_order = MMSimOrderBook._create_next_book_event(self.change_order_generator, env)
                next_expire = self._next_book_expiry(env)
            elif next_cancel_order in result.keys():
                # Note that cancellation can not cause spread crossing so there is no
                # need to match orders after this event.
                self._handle_cancel_order(env, result[next_cancel_order])
                next_cancel_order = MMSimOrderBook._create_next_book_event(self.cancel_order_generator, env)
                next_expire = self._next_book_expiry(env)
            elif next_expire in result.keys():
                # Note that expiration can not cause spread crossing so there is no
                # need to match orders after this event.
                result = self._handle_expire_order(env, result[next_expire])
                if result is not None and result['origin'] == 'strategy':
                    self.oms.order_action(dict(time=env.now, action='expired', order_id=result['order_id'],
                                               type_id=self.type_id))
                next_expire = self._next_book_expiry(env)

    def strategy_place_order(self, env, order_event):
        """
        Insert new order from strategy.
        
        :param env: simpy environment
        :param order_event: dictionary representing strategy order. 
        """
        bid = order_event['buy']
        side = self.bid if bid else self.ask
        expire_time = env.now + (order_event['duration'] * 24 * 60 * 60)
        price = order_event['price']
        order_id = self.next_order_id
        self.next_order_id += 1
        new_order = dict(type_id=self.type_id, order_id=order_id, issue_time=env.now,
                         buy=bid, duration=order_event['duration'], expire_time=expire_time,
                         price=price, min_volume=order_event['min_volume'], volume=order_event['volume'],
                         origin='strategy', trade_order=False)
        position = 0
        while position < len(side) and ((bid and side[position]['price'] > price) or
                                        (not bid and side[position]['price'] < price)):
            position += 1
        side.insert(position, new_order)
        self.oms.order_action(dict(time=env.now, action='created', order_id=order_id, type_id=self.type_id,
                                   issue_time=env.now, buy=bid, duration=order_event['duration'],
                                   expire_time=expire_time, price=price, min_volume=order_event['min_volume'],
                                   volume=order_event['volume'], origin='strategy', trade_order=False))
        # NOTE: If this order crosses the spread, then we may generate fills before this function call
        # returns.  The OMS should therefore be coded to record the order based on the order_action call
        # placed just before this function returns.
        self._match_orders(env)

    def strategy_cancel_order(self, env, order_id):
        """
        Cancel order placed by strategy.

        :param env: simpy environment
        :param order_id: order_id of order to cancel
        :except: throws an Exception if the specified order ID can not be found.
        """
        # Find the target order
        def find_order(order_list):
            for i in range(len(order_list)):
                next_order = order_list[i]
                if next_order['order_id'] == order_id and next_order['origin'] == 'strategy':
                    return next_order, i
            return None, None
        bid = True
        order, position = find_order(self.bid)
        if order is None:
            bid = False
            order, position = find_order(self.ask)
        if order is None:
            raise Exception("order_id not found")
        side = self.bid if bid else self.ask
        side.pop(position)
        self.oms.order_action(dict(time=env.now, action='canceled', order_id=order_id, type_id=self.type_id))

    def strategy_change_order(self, env, order_id, new_price):
        """
        Change the price of an existing order.

        :param env: simpy environment
        :param order_id: order_id of order to change
        :param new_price: new order price
        :except: throws an Exception if the specified order ID can not be found.
        """
        # Find the target order
        def find_order(order_list):
            for el in range(len(order_list)):
                next_order = order_list[el]
                if next_order['order_id'] == order_id and next_order['origin'] == 'strategy':
                    return next_order, el
            return None, None
        bid = True
        order, position = find_order(self.bid)
        if order is None:
            bid = False
            order, position = find_order(self.ask)
        if order is None:
            raise Exception("order_id not found")
        # Modify the price and move to the correct position on the side
        old_price = order['price']
        order['price'] = new_price
        order['issue_time'] = env.now
        order['expire_time'] = env.now + (order['duration'] * 24 * 60 * 60)
        side = self.bid if bid else self.ask
        side.pop(position)
        insert_position = len(side)
        for i in range(len(side)):
            if (bid and side[i]['price'] < new_price) or (not bid and side[i]['price'] > new_price):
                insert_position = i
                break
        side.insert(insert_position, order)
        self.oms.order_action(dict(time=env.now, action='change', order_id=order_id,
                                   old_price=old_price, new_price=new_price, type_id=self.type_id))
        self._match_orders(env)

    def strategy_buy(self, env, volume):
        """
        Allow the strategy to buy at the current best market price.

        :param env: SimPy Environment
        :param volume: the volume to buy, may be partially filled
        :return: An array of the form [(price, volume), ..., (price, volume)] giving the prices and volumes
        of assets purchased.  This array will be empty if no assets could be purchased.
        """
        to_buy = volume
        bought = []
        while to_buy > 0:
            if len(self.ask) == 0:
                break

            # Formulate a trade recorder and insert a bid equal to the top ask
            bid_price = self.ask[0]['price']
            trade_order = dict(type_id=self.type_id, order_id=self.next_order_id, issue_time=env.now,
                               buy=True, duration=1, expire_time=env.now, price=bid_price, min_volume=1,
                               volume=to_buy, origin='strategy', trade_order=True)
            self.next_order_id += 1
            self.bid.insert(0, trade_order)
            trade_recorder = TradeRecorder()
            self._match_orders(env, trade_recorder)
            if len(trade_recorder.trades) == 0:
                break
            for trade in trade_recorder.trades:
                next_price = trade['price']
                next_vol = trade['volume']
                to_buy -= next_vol
                bought.append((next_price, next_vol))

        return bought
