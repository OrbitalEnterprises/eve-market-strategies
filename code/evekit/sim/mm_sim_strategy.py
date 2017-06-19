"""
Market Making Simulator Strategy base class

This class provides convenience functions for implementing a strategy to be tested in the market
maker simulator.  Use of this class is optional.
"""
import pandas as pd


class MMSimStrategyBase:

    def __init__(self, oms, tax_rate, broker_rate, order_change_fee):
        self.oms = oms
        self.tax_rate = tax_rate
        self.broker_rate = broker_rate
        self.order_change_fee = order_change_fee
        self.order_map = {}

    @staticmethod
    def best_bid(book):
        if book.size == 0:
            return None
        top = book[book.buy == True]
        if top.size > 0:
            return top.iloc[0]['price']
        else:
            return None

    @staticmethod
    def best_ask(book):
        if book.size == 0:
            return None
        top = book[book.buy == False]
        if top.size > 0:
            return top.iloc[0]['price']
        else:
            return None

    def tracked_order(self, type_id, duration, buy, price, volume, min_volume):
        new_order = self.oms.order(type_id, duration, buy, price, volume, min_volume)
        order_id = new_order.order_id
        self.order_map[order_id] = new_order
        return new_order

    def promote_order(self, order, order_book, side_limit=None):
        side = order.buy
        best = self.best_bid(order_book) if side else self.best_ask(order_book)
        if best is not None:
            by_side = order_book[order_book.buy == side]
            if by_side.iloc[0]['order_id'] != order.order_id:
                # No longer top, reposition
                price = by_side.iloc[0]['price'] + (1 if side else -1) * 0.01
                if side_limit is None or (side and price <= side_limit) or (not side and price >= side_limit):
                    order.change(price)
                    return price
        return None

    def order_dataframe(self):
        orders = list(self.order_map.values())
        orders.sort(key=lambda x: x.original_issue_time)
        df_orders = []
        for o in orders:
            df_orders.append(dict(time=o.original_issue_time, type_id=o.type_id, status=o.status, buy=o.buy,
                                  price=o.price, volume=o.volume, volume_remaining=o.volume_remaining,
                                  gross=o.gross, tax=o.sales_tax, broker_fee=o.broker_fees))
        return pd.DataFrame(df_orders, index=[x['time'] for x in df_orders])

    def strategy_summary(self):
        orders = list(self.order_map.values())
        orders.sort(key=lambda x: x.original_issue_time)
        result = "{0:98s}\n".format("-" * 98)
        result += "{0:^98s}\n\n".format("Strategy Trading Summary")
        result += "{0:>10s} | {1:25s} | {2:>8s} | {3:>10s} | {4:>15s} | {5:>15s}\n".format("Type", "Status", "Side",
                                                                                           "Price", "Volume", "PNL")
        result += "{0:85s}\n".format("-" * 98)
        fmt_string = "{0:10d} | {1:25s} | {2:>8s} | {3:>10.2f} | {4:>15d} | {5:>15.2f}\n"
        pnl = 0
        for o in orders:
            side = 'Buy' if o.buy else 'Sell'
            pnl += o.net()
            result += fmt_string.format(o.type_id, o.status, side, o.price, o.volume, pnl)
        return result

    def run(self):
        """
        Main strategy execution method.  Subclasses should override this method to implement their strategy.
        """
        pass

