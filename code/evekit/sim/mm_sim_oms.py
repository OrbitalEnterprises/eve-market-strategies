"""
Market Making Simulator OMS

This component is the main controller in our market making simulator.  The OMS is responsible for initializing
the simulation, and also implements the methods that the strategy under test uses to send orders.
"""
from enum import Enum
from evekit.sim import MMSimOrderBook
import simpy


class MMOrderStatus(Enum):
    OPEN = 1
    FILLED = 2
    CANCELLED = 3
    EXPIRED = 4


class MMSimOrder:

    def __init__(self, env, oms, order_id, type_id, issue_time, duration, buy, price, volume, min_volume, broker_rate):
        self.order_id = order_id
        self.type_id = type_id
        self.issue_time = self.original_issue_time = issue_time
        self.duration = duration
        self.buy = buy
        self.price = price
        self.volume = volume
        self.volume_remaining = volume
        self.min_volume = min_volume
        self.status = MMOrderStatus.OPEN
        self.status_event = simpy.Event(env)
        self.env = env
        self.oms = oms
        self.broker_fees = price * volume * broker_rate
        self.sales_tax = 0
        self.gross = 0

    def gross(self):
        return self.gross

    def net(self):
        return self.gross - self.broker_fees - self.sales_tax

    def closed(self):
        """
        Return an event that triggers when it is no longer open.
        :return: an simpy event which is triggered when the order is no longer open
        """
        return self.status_event

    def cancel(self):
        """
        Cancel this order.  Silently ignored if the order is no longer open.
        """
        if self.status != MMOrderStatus.OPEN:
            return
        self.oms.cancel_order(self)

    def change(self, new_price):
        """
        Change the price of this order.  Silently ignored if the order is no longer open
        :param new_price: new price for order.
        """
        if self.status != MMOrderStatus.OPEN:
            return
        self.oms.change_order(self, new_price)

    def oms_cancel(self):
        """
        Called by the OMS to cancel.  Status and event are updated.
        """
        if self.status != MMOrderStatus.OPEN:
            raise Exception('Order not open!')
        self.status = MMOrderStatus.CANCELLED
        self.status_event.succeed()

    def oms_expire(self):
        """
        Called by the OMS to expire an order.  Status and event are updated
        """
        if self.status != MMOrderStatus.OPEN:
            raise Exception('Order not open!')
        self.status = MMOrderStatus.EXPIRED
        self.status_event.succeed()

    def oms_change(self, new_issue_time, new_price, broker_rate, change_fee):
        """
        Called by the OMS to record a price change.  Additional broker fees are applied
        if needed.
        
        :param new_issue_time:
        :param new_price: 
        :param broker_rate: 
        """
        if self.status != MMOrderStatus.OPEN:
            raise Exception('Order not open!')
        self.issue_time = new_issue_time
        self.broker_fees += change_fee
        price_delta = new_price - self.price
        if price_delta > 0:
            self.broker_fees += price_delta * self.volume_remaining * broker_rate
        self.price = new_price

    def oms_add_fill(self, volume, fill_price, tax_rate):
        """
        Called by the OMS to add fill data.  If this is the last fill,
        then the order will change status and the status event will be triggered.
        
        :param volume: volume filled 
        :param fill_price: price of fill
        :param tax_rate: tax rate applied to fill
        """
        if self.status != MMOrderStatus.OPEN:
            raise Exception('Order not open!')
        self.volume_remaining -= volume
        gross = volume * fill_price * (-1 if self.buy else 1)
        self.gross += gross
        if not self.buy:
            tax = gross * tax_rate
            self.sales_tax += tax
        if self.volume_remaining == 0:
            self.status = MMOrderStatus.FILLED
            self.status_event.succeed()


class MMSimOMS:

    # Time, in seconds, before an order can be changed or canceled
    ORDER_MODIFY_LIMIT = 300

    def __init__(self, env, type_init_map, tax_rate, broker_rate, order_change_fee, seed, debug=False):
        self.env = env
        self.debug = debug
        self.tax_rate = tax_rate
        self.broker_rate = broker_rate
        self.order_change_fee = order_change_fee
        self.type_map = {}
        self.seed = seed
        self.orders = {}
        self.active_event = None
        for k, v in type_init_map.items():
            book_data = {
                'order_book': MMSimOrderBook(v['ref_price'], v['ref_spread'], k, v['trades'], v['orders'], self, seed),
                'total_trades': 0,
                'total_volume': 0,
                'weighted': 0,
                'low_price': None,
                'high_price': None
            }
            self.type_map[k] = book_data
            book_data['order_book'].warmup(env, 100)
            env.process(book_data['order_book'].run(env))
        self.waiting_snaps = {}
        self.tracked_orders = {}

    def is_tracked_order(self, type_id, order_id):
        return type_id in self.tracked_orders and order_id in self.tracked_orders[type_id]

    def add_tracked_order(self, type_id, order_id, val):
        if type_id not in self.tracked_orders:
            self.tracked_orders[type_id] = {}
        self.tracked_orders[type_id][order_id] = val

    def remove_tracked_order(self, type_id, order_id):
        if type_id not in self.tracked_orders:
            return
        del self.tracked_orders[type_id][order_id]

    def record_trade(self, trade):
        t_type_id = trade['type_id']
        book = self.type_map[t_type_id]
        book['total_trades'] += 1
        book['total_volume'] += trade['volume']
        book['weighted'] += trade['volume'] * trade['price']
        book['low_price'] = min(book['low_price'] or trade['price'], trade['price'])
        book['high_price'] = max(book['high_price'] or trade['price'], trade['price'])
        # Update any strategy orders
        if self.is_tracked_order(t_type_id, trade['ask_id']) or self.is_tracked_order(t_type_id, trade['bid_id']):
            order_id = trade['ask_id'] if self.is_tracked_order(t_type_id, trade['ask_id']) else trade['bid_id']
            self.tracked_orders[t_type_id][order_id].oms_add_fill(trade['volume'], trade['price'], self.tax_rate)
        if self.debug:
            print("TRADE:" + str(trade))

    def order_action(self, action):
        if self.active_event is not None and action['action'] == 'created' and action['origin'] == 'strategy':
            # Order just created, create object for return from order method below
            order_id = action['order_id']
            self.active_event = MMSimOrder(self.env, self, action['order_id'], action['type_id'], action['issue_time'],
                                           action['duration'], action['buy'], action['price'], action['volume'],
                                           action['min_volume'], self.broker_rate)
            self.add_tracked_order(action['type_id'], order_id, self.active_event)
        if action['action'] == 'filled' and self.is_tracked_order(action['type_id'], action['order_id']):
            self.remove_tracked_order(action['type_id'], action['order_id'])
        if self.debug:
            print("ORDER:" + str(action))

    def new_snapshot(self, env, type_id, snap):
        if type_id in self.waiting_snaps:
            event = self.waiting_snaps[type_id]
            del self.waiting_snaps[type_id]
            event.succeed(snap)

    def order_book(self, type_id):
        """
        Provide an event which is triggered when the next book snapshot is
        available for the given type_id.
        
        :param type_id: the type_id to wait for 
        :return: an Event which is triggered when the book is available (the value will be the requested book)
        """
        if type_id in self.waiting_snaps:
            return self.waiting_snaps[type_id]
        book_event = simpy.Event(self.env)
        self.waiting_snaps[type_id] = book_event
        return book_event

    def get_current_order_book(self, type_id):
        book = self.type_map[type_id]
        return book['order_book'].dataframe()

    def order(self, type_id, duration, buy, price, volume, min_volume):
        self.active_event = {
            'buy': buy,
            'duration': duration,
            'price': price,
            'min_volume': min_volume,
            'volume': volume
        }
        book = self.type_map[type_id]
        book['order_book'].strategy_place_order(self.env, self.active_event)
        result = self.active_event
        self.active_event = None
        return result

    def change_order(self, order, new_price):
        if order.issue_time + MMSimOMS.ORDER_MODIFY_LIMIT > self.env.now:
            raise Exception("Order can not be changed yet!")
        book = self.type_map[order.type_id]
        book['order_book'].strategy_change_order(self.env, order.order_id, new_price)
        order.oms_change(self.env.now, new_price, self.broker_rate, self.order_change_fee)

    def cancel_order(self, order):
        if order.issue_time + MMSimOMS.ORDER_MODIFY_LIMIT > self.env.now:
            raise Exception("Order can not be canceled yet!")
        book = self.type_map[order.type_id]
        book['order_book'].strategy_cancel_order(self.env, order.order_id)
        order.oms_cancel()

    def buy(self, type_id, volume):
        """
        Buy assets at the current market price.

        :param type_id: the type ID of the assets to buy
        :param volume: desired buy amount
        :return: an array of the form [(price, volume), ..., (price, volume)] giving the number of
        assets purchased at each price.  This array will be empty if no assets were available to purchase.
        """
        pass

    def sell(self, type_id, volume):
        """
        Sell assets at the current market price

        :param type_id: the type ID of the assets to sell
        :param volume: desired sell amount
        :return: an array of the form [(price, volume, fee), ..., (price, volume, fee)] giving the number of
        assets sold at each price with fees.  This array will be empty if no orders were available to sell to.
        """
        pass

    def __str__(self):
        """
        Return trading summary organized by type_id
        """
        result = "{0:74s}\n".format("-"*86)
        result += "{0:^74s}\n\n".format("OMS Trading Summary")
        result += "{0:>10s} | {1:>10s} | {2:>15s} | {3:>12s} | {4:>12s} | {5:>12s}\n".\
            format("Type ID", "Trades", "Volume", "Low", "High", "VWAP")
        result += "{0:74s}\n".format("-"*86)
        fmt_string = "{0:10d} | {1:10d} | {2:15d} | {3:12.2f} | {4:12.2f} | {5:12.2f}\n"
        for k, v in self.type_map.items():
            vwap = v['weighted'] / v['total_volume']
            result += fmt_string.format(k, v['total_trades'], v['total_volume'], v['low_price'], v['high_price'], vwap)
        return result
