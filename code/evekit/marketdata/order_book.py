# evekit.marketdata.OrderBook module
"""
Retrieve and manipulate order books in various ways
"""
import os
import gzip
import urllib.error
import urllib.request
import datetime
import io
from pandas import DataFrame
from evekit.util import convert_raw_time
from evekit.reference import Client
from bravado.exception import HTTPError


class MarketOrder:
    """
    Order book market order
    """
    def __init__(self, order_string=None):
        if order_string is None:
            return
        vals = order_string.split(',')
        self.order_id = int(vals[0])
        self.buy = vals[1] == 'true' or vals[1] == 'True'
        raw_time = int(vals[2])
        self.issued = convert_raw_time(raw_time)
        self.price = float(vals[3])
        self.volume_entered = int(vals[4])
        self.min_volume = int(vals[5])
        self.volume = int(vals[6])
        self.order_range = vals[7]
        self.location_id = int(vals[8])
        self.duration = int(vals[9])

    def copy(self):
        new_order = MarketOrder()
        new_order.order_id = self.order_id
        new_order.buy = self.buy
        new_order.issued = self.issued           
        new_order.price = self.price            
        new_order.volume_entered = self.volume_entered   
        new_order.min_volume = self.min_volume       
        new_order.volume = self.volume           
        new_order.order_range = self.order_range      
        new_order.location_id = self.location_id      
        new_order.duration = self.duration         
        return new_order
        
    def __str__(self):
        return "MarkerOrder[%d, %s, %s, %s, %d, %d, %d, %s, %d, %d]" % (self.order_id, self.buy, self.issued,
                                                                        self.price, self.volume_entered,
                                                                        self.min_volume, self.volume, self.order_range,
                                                                        self.location_id, self.duration)

    def __repr__(self):
        return str(self)

    @staticmethod
    def __from_service__(json_result):
        init_string = "%d,%s,%d,%f,%d,%d,%d,%s,%d,%d" % (json_result['orderID'], json_result['buy'],
                                                         json_result['issued'], json_result['price'],
                                                         json_result['volumeEntered'], json_result['minVolume'],
                                                         json_result['volume'], json_result['orderRange'],
                                                         json_result['locationID'], json_result['duration'])
        return MarketOrder(init_string)


class MarketSnapshot:
    """
    Order book snapshot
    """
    def __init__(self, snapshot_time):
        self.snapshot_time = snapshot_time
        self.bid = []
        self.ask = []

    def contains(self, order):
        return order.order_id in [x.order_id for x in self.bid + self.ask]
    
    def add_bid(self, bid):
        self.bid.append(bid)

    def add_ask(self, ask):
        self.ask.append(ask)

    def insert_bid(self, bid):
        # Bids ordered by price descending
        if len(self.bid) == 0:
            self.add_bid(bid)
        else:
            for i in range(len(self.bid)):
                if self.bid[i].price < bid.price:
                    break
            self.bid[i:i] = [bid]

    def insert_ask(self, ask):
        # Asks ordered by price ascending
        if len(self.ask) == 0:
            self.add_ask(ask)
        else:
            for i in range(len(self.ask)):
                if self.ask[i].price > ask.price:
                    break
            self.ask[i:i] = [ask]

    def insert_order(self, order):
        if order.buy:
            self.insert_bid(order)
        else:
            self.insert_ask(order)

    def __str__(self):
        result = "MarketSnapshot[time=%s, bidCount=%d, askCount=%d,\n" % (
            self.snapshot_time, len(self.bid), len(self.ask))
        result += "Bids:\n"
        for bid in self.bid:
            result += str(bid) + "\n"
        result += "Asks: \n"
        for ask in self.ask:
            result += str(ask) + "\n"
        result += "]"
        return result

    def __repr__(self):
        return str(self)

    @staticmethod
    def __from_service__(json_result):
        snapshot_time = convert_raw_time(json_result['bookTime'])
        new_snap = MarketSnapshot(snapshot_time)
        for next_order in json_result['orders']:
            order_obj = MarketOrder.__from_service__(next_order)
            if order_obj.buy:
                new_snap.add_bid(order_obj)
            else:
                new_snap.add_ask(order_obj)
        return new_snap


def __dline__(ps):
    next_line = ps.readline().strip()
    return next_line.decode('utf-8')


class OrderBook:
    """
    OrderBook snapshots for a given type on a given date, optionally filtered to a specific set of regions.
    """
    def __init__(self, dt, size=5, ps=None, region_id=None):
        """
        Initialize order book from stream (if present).

        :param dt: datetime for day represented by order book
        :param size: interval size in minutes
        :param ps: optional character stream to read data from
        :param region_id: optional set of region IDs to include.  If None, then include all regions contained
                          in the stream.
        """
        self.date = dt
        self.interval_size = size
        if ps is None:
            return
        self.type_id = int(__dline__(ps))
        snapshot_count = int(__dline__(ps))
        # Read regions until EOF
        self.region = {}
        next_region = __dline__(ps)
        while len(next_region) > 0:
            next_region = int(next_region)
            snaps = []
            for i in range(snapshot_count):
                raw_time = int(__dline__(ps))
                snapshot_time = convert_raw_time(raw_time)
                bid_count = int(__dline__(ps))
                ask_count = int(__dline__(ps))
                next_snap = MarketSnapshot(snapshot_time)
                for j in range(bid_count):
                    next_line = __dline__(ps)
                    if region_id is None or next_region in region_id:
                        next_snap.add_bid(MarketOrder(next_line))
                for j in range(ask_count):
                    next_line = __dline__(ps)
                    if region_id is None or next_region in region_id:
                        next_snap.add_ask(MarketOrder(next_line))
                if region_id is None or next_region in region_id:
                    snaps.append(next_snap)
            # Store new region
            if region_id is None or next_region in region_id:
                self.region[next_region] = snaps
            if region_id is not None and len(self.region.keys()) == len(region_id):
                # Short circuit, we have all the regions we want
                break
            # Iterate to next region
            next_region = __dline__(ps)

    def __str__(self):
        result = "OrderBook[date=%s, intervalSize=%d, typeID=%d,\n" % (self.date, self.interval_size, self.type_id)
        for region in self.region.keys():
            result += "regionID=%d:\n" % (region)
            result += str(self.region[region])
        result += "]"
        return result

    def __repr__(self):
        return str(self)

    """
    Copy an order into previous snapshots starting from index and working
    backwards until we find a snapshot that either already contains the order,
    or has a timestamp before the issue date of the new order.
    """
    def __backfill_order__(self, order, region_id, index):
        issued = order.issued
        snaps = self.region[region_id]
        for i in range(index, -1, -1):
            next_snap = snaps[i]
            if next_snap.snapshot_time < issued or next_snap.contains(order):
                return
            order_copy = order.copy()
            next_snap.insert_order(order_copy)
    
    """
    Look for order gapping and backfill to fix.
    """
    def fill_gaps(self):
        for region_id in self.region.keys():
            # Cycle through snapshots in pairs, look for orders we need to backfill
            snap_list = self.region[region_id]
            for i in range(0, len(snap_list) - 1):
                current_snap = snap_list[i]
                current_time = current_snap.snapshot_time
                next_snap = snap_list[i+1]
                next_time = next_snap.snapshot_time
                #
                # Look for new orders added in the next snapshot
                #
                all_current_orders = current_snap.bid + current_snap.ask
                all_new_orders = next_snap.bid + next_snap.ask
                new_id_set = set([x.order_id for x in all_new_orders]).difference(set([x.order_id for x in all_current_orders]))
                if len(new_id_set) > 0:
                    for next_order in all_new_orders:
                        if next_order.order_id in new_id_set and next_order.issued < current_time:
                            # Gap - backfill
                            self.__backfill_order__(next_order, region_id, i)
    
    @staticmethod
    def __read_index__(fobj, max_offset):
        """
        Read order book index file and return a map from type to offsets.
        :param fobj: file object to read from
        :param max_offset: max offset to report for last value
        :return: map from type to array of offsets
        """
        result = {}
        last_type = -1
        for line in gzip.GzipFile(fileobj=fobj).readlines():
            line = line.decode('utf-8')
            fields = line.split(" ")
            type_id = int((fields[0].split("_"))[1])
            offset = int(fields[1])
            result[type_id] = [offset, -1]
            if last_type != -1:
                result[last_type][1] = offset - 1
            last_type = type_id
            if last_type != -1:
                result[last_type][1] = max_offset
        return result

    @staticmethod
    def __read_bulk_file__(target_date, types, regions, parent_dir=".", is_tree=True):
        """
        Extract the specified types and regions out of a bulk market history local file
        :param target_date: date to extract
        :param types: array-like of types to extract
        :param regions: array-like of regions to extract
        :param parent_dir: parent directory where local files are stored
        :param is_tree: if true, market history is organized as a tree
        :return: array of extracted MarketHistory objects
        """
        path_string = "%04d/%02d/%02d" % (target_date.year, target_date.month, target_date.day)
        date_string = "%04d%02d%02d" % (target_date.year, target_date.month, target_date.day)
        bulk_file = parent_dir + "/" + (path_string if is_tree else "") + "/interval_" + date_string + "_5.bulk"
        index_file = parent_dir + "/" + (path_string if is_tree else "") + "/interval_" + date_string + "_5.index.gz"
        if (not os.path.exists(bulk_file)) or (not os.path.exists(index_file)):
            return []
        results = []
        try:
            max_offset = os.stat(bulk_file).st_size
            index_map = OrderBook.__read_index__(open(index_file, 'rb'), max_offset)
            # If the number of requested types is above some threshold, then linearly scan
            # the bulk file as this will be substantially more efficient in time.
            if len(types) > 1500:
                # Scan the entire file, skipping types we don't care about
                sorted_map = []
                scanned = 0
                for x in index_map.keys():
                    sorted_map.append(dict(type=x, start=index_map[x][0], end=index_map[x][1]))
                sorted_map = sorted(sorted_map, key=lambda k: k['start'])
                fd = open(bulk_file, 'rb')
                for next_type in sorted_map:
                    start = next_type['start']
                    end = next_type['end']
                    buff = fd.read(end - start + 1)
                    scanned += 1
                    if next_type['type'] not in types:
                        continue
                    ps = gzip.GzipFile(fileobj=io.BytesIO(buff))
                    results.append(OrderBook(target_date, ps=ps, region_id=regions))
                    ps.close()
                    if scanned % 1000 == 0:
                        print("+", end='')
                    if len(results) == len(types):
                        # All types loaded, short circuit
                        break
                fd.close()
            else:
                # Handle one type at a type
                for next_type in types:
                    if next_type not in index_map:
                        continue
                    start = index_map[next_type][0]
                    end = index_map[next_type][1]
                    fd = open(bulk_file, 'rb')
                    fd.seek(start)
                    buff = fd.read(end - start + 1)
                    ps = gzip.GzipFile(fileobj=io.BytesIO(buff))
                    results.append(OrderBook(target_date, ps=ps, region_id=regions))
                    ps.close()
                    fd.close()
        except OSError:
            return []
        return results

    @staticmethod
    def __read_archive__(target_date, types, regions):
        """
        Read market history from archive.
        :param target_date: target date to retrieve
        :param types: array-like of types to retrieve
        :param regions: array-like of regions to retrieve
        :return: array of retrieved MarketHistory objects
        """
        date_string = "%04d%02d%02d" % (target_date.year, target_date.month, target_date.day)
        path_string = "%04d/%02d/%02d" % (target_date.year, target_date.month, target_date.day)
        bulk_file = "interval_" + date_string + "_5.bulk"
        index_file = "interval_" + date_string + "_5.index.gz"
        bulk_url = "https://storage.googleapis.com/evekit_md/" + path_string + "/" + bulk_file
        index_url = "https://storage.googleapis.com/evekit_md/" + path_string + "/" + index_file
        max_offset = -1
        results = []
        try:
            index_map = OrderBook.__read_index__(urllib.request.urlopen(index_url), max_offset)
            for next_type in types:
                if next_type not in index_map:
                    continue
                range_string = "bytes=" + str(index_map[next_type][0]) + "-"
                if index_map[next_type][1] != -1:
                    range_string += str(index_map[next_type][1])
                request = urllib.request.Request(bulk_url, headers={"Range": range_string})
                ps = gzip.GzipFile(fileobj=urllib.request.urlopen(request))
                results.append(OrderBook(target_date, ps=ps, region_id=regions))
                ps.close()
        except urllib.error.HTTPError:
            return []
        return results

    @staticmethod
    def __read_service__(target_date, types, regions):
        """
        Read order books from Orbital Enterprises market data service.  A separate call is made
        for each type, region and snapshot.  This is very inefficient for large sets of types or regions.
        Use carefully.  Also note that we arbitrarily select five minute snapshots for the given date
        starting from midnight (instead of using the actual snapshots available in the data, which is
        not known when using the market service).

        :param target_date: date for which order books will be retrieved
        :param types: array-like of types to retrieve
        :param regions: array-like of regions to retrieve
        :return: array of OrderBook results
        """
        five_minute_delta = datetime.timedelta(minutes=5)
        client = Client.MarketData.get()
        results = []
        for next_type in types:
            new_book = OrderBook(target_date)
            new_book.type_id = next_type
            new_book.region = {}
            for next_region in regions:
                snapshots = []
                current_time = target_date.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=datetime.timezone.utc)
                for _ in range(288):
                    try:
                        result, response = client.MarketData.book(typeID=next_type, regionID=next_region,
                                                                  date=str(current_time) + " UTC").result()
                        if response.status_code == 200:
                            snapshots.append(MarketSnapshot.__from_service__(result))
                    except HTTPError:
                        # ignore
                        pass
                    finally:
                        current_time = current_time + five_minute_delta
                # Create new OrderBook from list of snapshots
                new_book.region[next_region] = snapshots
            results.append(new_book)
        return results

    @staticmethod
    def get_day(date, types, regions, config=None):
        """
        Retrieve a single day of order book snapshots for the given types and regions.

        :param date: date to retrieve
        :param types: array-like of types for which order books will be retrieved.
        :param regions: array-like of regions for which order books will be retrieved.
        :param config: optional config parameter with settings:
          verbose - if True, show what we're doing when we do it
          skip_missing - if True, skip missing data, otherwise throw an exception
          local_storage - if present, gives the parent directory for local storage containing market history
          tree - if True, then local storage is organized as a date tree
          use_online - if True, use either the online archive or market data service to fill missing dates.
        :return: an array of order books for the given day for each of the specified types and regions.
        """
        results = []
        config = {} if config is None else config
        local_storage_dir = config.get('local_storage', '')
        use_local = len(local_storage_dir) > 0 and os.path.exists(local_storage_dir)
        use_online = config.get('use_online', True)
        verbose = config.get('verbose', False)
        skip_missing = config.get('skip_missing', True)
        # Try local storage first if present, then online sources if configured
        if use_local:
            if verbose:
                print("checking local source...", end="")
            is_tree = config.get('tree', False)
            values = OrderBook.__read_bulk_file__(date, types, regions, local_storage_dir, is_tree)
            results.extend(values)
        # Try online if no local storage, or local storage doesn't have data
        if len(results) == 0 and use_online:
            if verbose:
                print("checking online sources...", end="")
            # Try archive first
            values = OrderBook.__read_archive__(date, types, regions)
            if len(values) == 0:
                # Last chance, try the market service.  This will be very slow for large
                # amounts of data.
                values = OrderBook.__read_service__(date, types, regions)
            results.extend(values)
        # If still no data, then check whether we should complain
        if len(results) == 0 and not skip_missing:
            raise Exception("No data found for date %s" % date)
        return results

    @staticmethod
    def get_data_frame(dates, types, regions, config=None):
        """
        Retrieve order book snapshots into a DataFrame indexed by snapshot time.
        NOTE: this data can be very large.  Use the types and regions arguments
        to filter judiciously, and avoid selecting large date ranges.  The rows
        of the DataFrame are identical to market orders except that we add columns
        for type and region.

        :param dates: array-like date range to retrieve.
        :param types: array-like types for which orders will be retrieved.
        :param regions: array-like regions for which orders will be retrieved.
        :param config: optional config parameter with settings:
          verbose - if True, show what we're doing as we do it
          skip_missing - if True, skip dates for which data can not be found
          local_storage - if present, gives the parent directory for local storage containing order book data
          tree - if True, then local storage is organized as a date tree
          use_online - if True, use either the online archive or market data service to fill missing dates.
          fill_gaps - if True, fill gaps of missing orders
        :return: DataFrame containing the requested data indexed by book snapshot time.
        """
        config = {} if config is None else config
        verbose = config.get('verbose', False)
        fill_gaps = config.get('fill_gaps', False)
        # Turn off verbose in called methods
        config['verbose'] = False
        results = []
        for next_date in dates:
            if verbose:
                print("Retrieving %s" % (str(next_date)), end="...")
            results.extend(OrderBook.get_day(next_date, types, regions, config))
            if verbose:
                print("done")
        # Fix gaps if requested
        if fill_gaps:
            for ob in results:
                ob.fill_gaps()
        # Flatten order book snapshots into an array
        order_list = []
        for next_book in results:
            type_id = next_book.type_id
            for region_id in next_book.region.keys():
                for next_snap in next_book.region[region_id]:
                    snap_time = next_snap.snapshot_time
                    for next_order in next_snap.bid + next_snap.ask:
                        to_dict = next_order.__dict__
                        to_dict['date'] = snap_time
                        to_dict['type_id'] = type_id
                        to_dict['region_id'] = region_id
                        order_list.append(to_dict)
        return DataFrame(order_list, [x['date'] for x in order_list])
