# evekit.marketdata.MarketHistory module
"""
Retrieve and manipulate market history (daily market snapshots) in various ways
"""
import os
import gzip
import urllib.error
import urllib.request
from pandas import DataFrame
from evekit.util import convert_raw_time
from evekit.reference import Client
from bravado.exception import HTTPError


class MarketHistory:
    def __init__(self, history_string):
        vals = history_string.split(',')
        self.type_id = int(vals[0])
        self.region_id = int(vals[1])
        self.order_count = int(vals[2])
        self.low_price = float(vals[3])
        self.high_price = float(vals[4])
        self.avg_price = float(vals[5])
        self.volume = int(vals[6])
        raw_time = int(vals[7])
        self.date = convert_raw_time(raw_time)

    def __str__(self):
        return "MarketHistory[%d, %d, %d, %f, %f, %f, %d, %s]" % (self.type_id, self.region_id, self.order_count,
                                                                  self.low_price, self.high_price, self.avg_price,
                                                                  self.volume, self.date)

    def __repr__(self):
        return str(self)

    @staticmethod
    def __json_to_string__(json):
        """
        Convert json data returned by market data service to a string which can be parsed by the
        MarketHistory constructor.
        :param json: JSON format object returned from market data service.
        :return: string suitable for parsing by MarketData constructor
        """
        return "%d,%d,%d,%f,%f,%f,%d,%d" % (json['typeID'], json['regionID'], json['orderCount'],
                                            json['lowPrice'], json['highPrice'], json['avgPrice'],
                                            json['volume'], json['date'])

    @staticmethod
    def __read_row__(types, regions, fobj):
        """
        Extract market history rows for the given types and regions from the given file object
        :param types: array-like of types to extract
        :param regions: array-like of regions to extract
        :param fobj: file object to read from
        :return: array of extracted MarketHistory objects
        """
        results = []
        ps = gzip.GzipFile(fileobj=fobj)
        for line in ps.readlines():
            line = line.decode('utf-8')
            next_obj = MarketHistory(line)
            if next_obj.type_id in types and next_obj.region_id in regions:
                results.append(next_obj)
        ps.close()
        return results

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
        bulk_file = parent_dir + "/" + (path_string if is_tree else "") + "/market_" + date_string + ".bulk"
        if not os.path.exists(bulk_file):
            return []
        return MarketHistory.__read_row__(types, regions, open(bulk_file, 'rb'))

    @staticmethod
    def __read_index__(fobj, max_offset):
        """
        Read market history index file and return a map from type to offsets
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
        bulk_file = "market_" + date_string + ".bulk"
        index_file = "market_" + date_string + ".index.gz"
        bulk_url = "https://storage.googleapis.com/evekit_md/" + path_string + "/" + bulk_file
        index_url = "https://storage.googleapis.com/evekit_md/" + path_string + "/" + index_file
        max_offset = -1
        # Minor tuning optimization.  If less than this many types are requested then we use the
        # index file and make a separate call for each type.  Otherwise, we just read the entire
        # bulk file.
        type_count_threshold = 5
        results = []
        try:
            if len(types) < type_count_threshold:
                # Use the index map and make multiple requests
                index_map = MarketHistory.__read_index__(urllib.request.urlopen(index_url), max_offset)
                for next_type in types:
                    if next_type not in index_map:
                        continue
                    range_string = "bytes=" + str(index_map[next_type][0]) + "-"
                    if index_map[next_type][1] != -1:
                        range_string += str(index_map[next_type][1])
                    request = urllib.request.Request(bulk_url, headers={"Range": range_string})
                    results.extend(MarketHistory.__read_row__([next_type], regions, urllib.request.urlopen(request)))
            else:
                # Read the entire bulk file in one shot
                results.extend(MarketHistory.__read_row__(types, regions, urllib.request.urlopen(bulk_url)))
        except urllib.error.HTTPError:
            return []
        return results

    @staticmethod
    def __read_service__(target_date, types, regions):
        """
        Read market history from Orbital Enterprises market data service.  A separate call is made
        for each type and region.  This is very inefficient for large sets of types or regions.
        Use carefully.
        :param target_date: date for which history will be retrieved
        :param types: array-like of types to retrieve
        :param regions: array-like of regions to retrieve
        :return: array of MarketHistory results
        """
        client = Client.MarketData.get()
        results = []
        for next_type in types:
            for next_region in regions:
                try:
                    result, response = client.MarketData.history(typeID=next_type, regionID=next_region,
                                                                 date=str(target_date)).result()
                    if response.status_code != 200:
                        continue
                    results.append(MarketHistory(MarketHistory.__json_to_string__(result)))
                except HTTPError:
                    continue
        return results

    @staticmethod
    def get_day(date, types, regions, config=None):
        """
        Retrieve a single day of market history for the given types and regions.
        :param date: date to retrieve
        :param types: array-like of types for which history will be retrieved.
        :param regions: array-like of regions for which history will be retrieved.
        :param config: optional config parameter with settings:
          verbose - if True, show what we're doing when we do it
          as_dict - if True, convert MarketHistory objects to dictionaries before returning
          skip_missing - if True, skip missing data, otherwise throw an exception
          local_storage - if present, gives the parent directory for local storage containing market history
          tree - if True, then local st
          orage is organized as a date tree
          use_online - if True, use either the online archive or market data service to fill missing dates.
        :return: an array of market history for the given day for each of the specified types and regions.
        """
        results = []
        config = {} if config is None else config
        local_storage_dir = config.get('local_storage', '')
        use_local = len(local_storage_dir) > 0 and os.path.exists(local_storage_dir)
        use_online = config.get('use_online', True)
        verbose = config.get('verbose', False)
        skip_missing = config.get('skip_missing', True)
        as_dict = config.get('as_dict', False)
        # Try local storage first if present, then online sources if configured
        if use_local:
            if verbose:
                print("checking local source...", end="")
            is_tree = config.get('tree', False)
            values = MarketHistory.__read_bulk_file__(date, types, regions, local_storage_dir, is_tree)
            if as_dict:
                values = [x.__dict__ for x in values]
            results.extend(values)
        # Try online if no local storage, or local storage doesn't have data
        if len(results) == 0 and use_online:
            if verbose:
                print("checking online sources...", end="")
            # Try archive first
            values = MarketHistory.__read_archive__(date, types, regions)
            if len(values) == 0:
                # Last chance, try the market service
                values = MarketHistory.__read_service__(date, types, regions)
            if as_dict:
                values = [x.__dict__ for x in values]
            results.extend(values)
        # If still no data, then check whether we should complain
        if len(results) == 0 and not skip_missing:
            raise Exception("No data found for date %s" % date)
        return results

    @staticmethod
    def get_data_frame(dates, types, regions, config=None):
        """
        Retrieve market history into a DataFrame indexed by market history date.
        :param dates: array-like date range to retrieve.
        :param types: array-like types for which history will be retrieved.
        :param regions: array-like regions for which history will be retrieved.
        :param config: optional config parameter with settings:
          verbose - if True, show what we're doing as we do it
          skip_missing - if True, skip dates for which data can not be found
          local_storage - if present, gives the parent directory for local storage containing market history
          tree - if True, then local storage is organized as a date tree
          use_online - if True, use either the online archive or market data service to fill missing dates.
        :return: DataFrame contained the requested data indexed by market history date.
        """
        config = {} if config is None else config
        config['as_dict'] = True
        verbose = config.get('verbose', False)
        # Turn off verbose in called methods
        config['verbose'] = False
        results = []
        for next_date in dates:
            if verbose:
                print("Retrieving %s" % (str(next_date)), end="...")
            results.extend(MarketHistory.get_day(next_date, types, regions, config))
            if verbose:
                print("done")
        return DataFrame(results, [x['date'] for x in results])
