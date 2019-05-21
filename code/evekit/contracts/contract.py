# evekit.contracts.Contract module
"""
Retrieve and manipulate contracts in various ways
"""
import gzip
import os
import urllib.error
import urllib.request

from evekit.util import convert_raw_time


class ContractItem:
    """
    Item attached to item exchange contract
    """

    def __init__(self, item_string=None):
        if item_string is None:
            return
        vals = item_string.split(',')
        self.is_blueprint_copy = vals[0] == 'true'
        self.is_included = vals[1] == 'true'
        self.item_id = int(vals[2]) if vals[2] != 'null' else -1
        self.material_efficiency = int(vals[3]) if vals[3] != 'null' else -1
        self.quantity = int(vals[4])
        self.record_id = int(vals[5])
        self.runs = int(vals[6]) if vals[6] != 'null' else -1
        self.time_efficiency = int(vals[7]) if vals[7] != 'null' else -1
        self.type_id = int(vals[8])

    def copy(self):
        new_item = ContractItem()
        new_item.is_blueprint_copy = self.is_blueprint_copy
        new_item.is_included = self.is_included
        new_item.item_id = self.item_id
        new_item.material_efficiency = self.material_efficiency
        new_item.quantity = self.quantity
        new_item.record_id = self.record_id
        new_item.runs = self.runs
        new_item.time_efficiency = self.time_efficiency
        new_item.type_id = self.type_id
        return new_item

    def __str__(self):
        return "ContractItem[%s, %s, %d, %d, %d, %d, %d, %d, %d]" % (self.is_blueprint_copy,
                                                                     self.is_included,
                                                                     self.item_id,
                                                                     self.material_efficiency,
                                                                     self.quantity,
                                                                     self.record_id,
                                                                     self.runs,
                                                                     self.time_efficiency,
                                                                     self.type_id)

    def __repr__(self):
        return str(self)


class ContractBid:
    """
    Bid attached to auction contract
    """

    def __init__(self, bid_string=None):
        if bid_string is None:
            return
        vals = bid_string.split(',')
        self.amount = float(vals[0])
        self.bid_id = int(vals[1])
        self.date_bid = convert_raw_time(int(vals[2]))

    def copy(self):
        new_bid = ContractBid()
        new_bid.amount = self.amount
        new_bid.bid_id = self.bid_id
        new_bid.date_bid = self.date_bid
        return new_bid

    def __str__(self):
        return "ContractBid[%f, %d, %s]" % (self.amount,
                                            self.bid_id,
                                            self.date_bid)

    def __repr__(self):
        return str(self)


class Contract:
    """
    Single contract instance
    """

    def __init__(self, contract_string=None):
        if contract_string is None:
            return
        vals = contract_string.split(',')
        self.buyout = float(vals[0]) if vals[0] != 'null' else -1
        self.collateral = float(vals[1]) if vals[1] != 'null' else -1
        self.contract_id = int(vals[2])
        self.date_expired = convert_raw_time(int(vals[3]))
        self.date_issued = convert_raw_time(int(vals[4]))
        self.days_to_complete = int(vals[5])
        self.end_location_id = int(vals[6])
        self.for_corporation = vals[7] == 'true'
        self.issuer_corporation_id = int(vals[8])
        self.issuer_id = int(vals[9])
        self.price = float(vals[10])
        self.reward = float(vals[11])
        self.start_location_id = int(vals[12])
        # Title may have embedded commas which require some special handling
        self.title = ','.join(vals[13:13 + len(vals) - 15])
        self.contract_type = vals[-2]
        self.volume = float(vals[-1])

        # Information which can be resolved later
        self.items = None
        self.bids = None

        # Information needed for resolving items or bids
        self.contract_snap_time = None
        self.contract_region = None
        self.contract_local_dir = None

    def copy(self):
        new_contract = Contract()
        new_contract.buyout = self.buyout
        new_contract.collateral = self.collateral
        new_contract.contract_id = self.contract_id
        new_contract.date_expired = self.date_expired
        new_contract.date_issued = self.date_issued
        new_contract.days_to_complete = self.days_to_complete
        new_contract.end_location_id = self.end_location_id
        new_contract.for_corporation = self.for_corporation
        new_contract.issuer_corporation_id = self.issuer_corporation_id
        new_contract.issuer_id = self.issuer_id
        new_contract.price = self.price
        new_contract.reward = self.reward
        new_contract.start_location_id = self.start_location_id
        new_contract.title = self.title
        new_contract.contract_type = self.contract_type
        new_contract.volume = self.volume
        new_contract.items = [x.copy() for x in self.items]
        new_contract.bids = [x.copy() for x in self.bids]
        new_contract.contract_snap_time = self.contract_snap_time
        new_contract.contract_region = self.contract_region
        new_contract.contract_local_dir = self.contract_local_dir
        return new_contract

    def __str__(self):
        return "Contract[%f, %f, %d, %s, %s, %d, %d, %s, %d, %d, %f, %f, %d, %s, %s, %f]" % (self.buyout,
                                                                                             self.collateral,
                                                                                             self.contract_id,
                                                                                             self.date_expired,
                                                                                             self.date_issued,
                                                                                             self.days_to_complete,
                                                                                             self.end_location_id,
                                                                                             self.for_corporation,
                                                                                             self.issuer_corporation_id,
                                                                                             self.issuer_id,
                                                                                             self.price,
                                                                                             self.reward,
                                                                                             self.start_location_id,
                                                                                             self.title,
                                                                                             self.contract_type,
                                                                                             self.volume)

    def __repr__(self):
        return str(self)

    def expired(self):
        return convert_raw_time(self.contract_snap_time) >= self.date_expired

    def resolve_items(self):
        """
        If this is an item_exchange contract, then attempt to retrieve the items associated with this
        contract.  This may fail if the contract has already expired.  Fail silently if this is not
        an item_exchange contract.
        """
        if self.contract_type != 'item_exchange':
            # Contract not an item exchange
            return
        if self.expired():
            # Contract expired
            return
        if self.items is not None:
            # Already resolved
            return
        config = {}
        if self.contract_local_dir is not None:
            config['use_local'] = True
            config['local_storage'] = self.contract_local_dir
        self.items = Contract.__get_items_or_bids__(self.contract_id, convert_raw_time(self.contract_snap_time),
                                                    self.contract_region, config, items=True)

    def resolve_bids(self):
        """
        If this is an auction contract, then attempt to retrieve the bids associated with this contract.
        This may fail if the contract has already expired.  Fail silently if this is not an action
        contract.
        """
        if self.contract_type != 'auction':
            # Contract not an auction
            return
        if self.expired():
            # Contract expired
            return
        if self.bids is not None:
            # Already resolved
            return
        config = {}
        if self.contract_local_dir is not None:
            config['use_local'] = True
            config['local_storage'] = self.contract_local_dir
        self.bids = Contract.__get_items_or_bids__(self.contract_id, convert_raw_time(self.contract_snap_time),
                                                   self.contract_region, config, items=False)

    @staticmethod
    def __read_snapshot_file__(fname):
        """
        Extract a list of contracts from a snapshot file

        :param fname: path to file to read from.  The file is expected to be a gzip'd csv file
        where the first line is a header.
        :return: array of extracted Contract objects.
        """
        if not os.path.exists(fname):
            return []
        results = []
        try:
            fobj = open(fname, 'rb')
            for line in gzip.GzipFile(fileobj=fobj).readlines():
                line = line.decode('utf-8')
                if line.startswith('buyout'):
                    # Header line, skip
                    continue
                results.append(Contract(contract_string=line))
            fobj.close()
        except OSError:
            return []
        return results

    @staticmethod
    def __read_items_file__(fname):
        """
        Extract a list of contract items from an items file

        :param fname: path to file to read from.  The file is expected to be a plain txt file
        in csv format where the first line is a header.
        :return: array of extracted ContractItem objects.
        """
        if not os.path.exists(fname):
            return []
        results = []
        try:
            fobj = open(fname, 'r')
            for line in fobj.readlines():
                if line.startswith('is_blueprint_copy'):
                    # Header line, skip
                    continue
                results.append(ContractItem(item_string=line))
            fobj.close()
        except OSError:
            return []
        return results

    @staticmethod
    def __read_bids_file__(fname):
        """
        Extract a list of contract bids from a bids file

        :param fname: path to file to read from.  The file is expected to be a plain txt file
        in csv format where the first line is a header.
        :return: array of extracted ContractBid objects.
        """
        if not os.path.exists(fname):
            return []
        results = []
        try:
            fobj = open(fname, 'r')
            for line in fobj.readlines():
                if line.startswith('amount'):
                    # Header line, skip
                    continue
                results.append(ContractBid(bid_string=line))
            fobj.close()
        except OSError:
            return []
        return results

    @staticmethod
    def __read_local_snapshots__(region_id, src_dir=None):
        """
        Retrieve a list of pairs (timestamp, list of contracts) from a local directory for the
        given region ID.  The list of pairs will be in timestamp order.

        :param region_id: the region for which snapshots will be retrieved
        :param src_dir: parent directory of region files
        :return: a list of pairs (timestamp, list of contracts) in timestamp order.
        """
        parent_dir = '/home/orbital/snaps/contract_regions' if src_dir is None else src_dir
        src = parent_dir + '/' + str(region_id)
        # Find latest file at target location and read in contracts
        latest = None
        latest_time = 0
        for fileName in os.listdir(src):
            if not fileName.startswith('region_contracts_'):
                # Skip non-snapshot files
                continue
            if fileName[-3:] != '.gz':
                # Skip partially written gzip files
                continue
            tstamp = int(fileName.split('_')[2])
            if latest is None or tstamp > latest_time:
                latest = fileName
                latest_time = tstamp
        if latest is None:
            raise RuntimeError("No latest snapshot file found at location: " + src)
        # Return result object
        contracts = Contract.__read_snapshot_file__(src + '/' + latest)
        for cc in contracts:
            cc.contract_snap_time = latest_time
            cc.contract_region = region_id
            cc.contract_local_dir = parent_dir
        return latest_time, contracts

    @staticmethod
    def __read_local_items__(contract_id, region_id, src_dir=None):
        parent_dir = '/home/orbital/snaps/contract_regions' if src_dir is None else src_dir
        src = parent_dir + '/' + str(region_id)
        # Find items file and return item entries
        src = src + '/' + 'contract_' + str(contract_id) + '_items.txt'
        # Return result object
        return Contract.__read_items_file__(src)

    @staticmethod
    def __read_local_bids__(contract_id, region_id, src_dir=None):
        parent_dir = '/home/orbital/snaps/contract_regions' if src_dir is None else src_dir
        src = parent_dir + '/' + str(region_id)
        # Find items file and return bid entries
        src = src + '/' + 'contract_' + str(contract_id) + '_bids.txt'
        # Return result object
        return Contract.__read_bids_file__(src)

    @staticmethod
    def __read_contract_snaps_index__(date):
        index_url = "https://storage.googleapis.com/evekit_md/%d/%02d/%02d/contract_snapshots_%s_30.index" % \
                    (date.year, date.month, date.day, date.strftime("%Y%m%d"))
        try:
            ps = urllib.request.urlopen(index_url)
            result = {}
            last_region = -1
            for line in ps.readlines():
                line = line.decode('utf-8')
                fields = line.split(" ")
                region_id_txt = (fields[0].split("_"))[4]
                region_id = int(region_id_txt[:-3])
                offset = int(fields[1])
                result[region_id] = [offset, -1]
                if last_region != -1:
                    result[last_region][1] = offset - 1
                last_region = region_id
            return result
        except urllib.error.URLError:
            return {}

    @staticmethod
    def __read_contract_data_index__(date):
        index_url = "https://storage.googleapis.com/evekit_md/%d/%02d/%02d/contract_data_%s.index.gz" % \
                    (date.year, date.month, date.day, date.strftime("%Y%m%d"))
        try:
            ps = urllib.request.urlopen(index_url)
            result = {}
            last_contract = -1
            for line in gzip.GzipFile(fileobj=ps).readlines():
                line = line.decode('utf-8')
                fields = line.split(" ")
                contract_id_txt = (fields[0].split("_"))[2]
                contract_id = int(contract_id_txt[:-7])
                offset = int(fields[1])
                result[contract_id] = [offset, -1]
                if last_contract != -1:
                    result[last_contract][1] = offset - 1
                last_contract = contract_id
            return result
        except urllib.error.URLError:
            return {}

    @staticmethod
    def __read_bulk_stream__(fs, region_id):
        """
        Read contract snapshots from a bulk stream.  Returns a list of pairs (timestamp, list of contracts)
        in timestamp order.

        :param fs: Open filestream from which bulkdata will be read.
        :return: a list of pairs (timestamp, list of contracts) in timestamp order
        """
        snapshot_count = int(__dline__(fs))
        results = []
        for _ in range(snapshot_count):
            next_ts = int(__dline__(fs)) * 1000
            contract_count = int(__dline__(fs))
            contracts = []
            for _ in range(contract_count):
                next_contract = Contract(contract_string=__dline__(fs))
                next_contract.contract_snap_time = next_ts
                next_contract.contract_region = region_id
                contracts.append(next_contract)
            results.append((next_ts, contracts))
        return results

    @staticmethod
    def __read_item_bulk_stream__(fs):
        """
        Read contract items from a bulk stream.  Returns a list ContractItem.

        :param fs: Open filestream from which bulk data will be read.
        :return: a list of ContractItem
        """
        results = []
        line = __dline__(fs)
        while line != '':
            results.append(ContractItem(item_string=line))
            line = __dline__(fs)
        return results

    @staticmethod
    def __read_bid_bulk_stream__(fs):
        """
        Read contract items from a bulk stream.  Returns a list ContractItem.

        :param fs: Open filestream from which bulk data will be read.
        :return: a list of ContractItem
        """
        results = []
        line = __dline__(fs)
        while line != '':
            results.append(ContractBid(bid_string=line))
            line = __dline__(fs)
        return results

    @staticmethod
    def __read_item_or_bid_archive__(target_date, contract_id, index=None, items=True):
        """
        Read contract items or bids from archive.

        :param target_date: target date to retrieve
        :param contract_id: contract ID of items or bids to retrieve
        :param index: if not None, then the contract data bulk file index for this date
        :return: a list of ContractItem or ContractBid for the given contract (if found, otherwise an empty list)
        """
        date_string = "%04d%02d%02d" % (target_date.year, target_date.month, target_date.day)
        path_string = "%04d/%02d/%02d" % (target_date.year, target_date.month, target_date.day)
        bulk_file = "contract_data_" + date_string + ".bulk"
        bulk_url = "https://storage.googleapis.com/evekit_md/" + path_string + "/" + bulk_file
        if index is None:
            index = Contract.__read_contract_data_index__(target_date)
        if contract_id not in index.keys():
            return []
        sorted_keys = list(index.keys())
        sorted_keys.sort()
        try:
            range_string = "bytes=" + str(index[contract_id][0]) + "-"
            if index[contract_id][1] != -1 and contract_id != sorted_keys[-1]:
                # On the last contract ID, we need to leave an open range request
                range_string += str(index[contract_id][1])
            request = urllib.request.Request(bulk_url, headers={"Range": range_string})
            ps = gzip.GzipFile(fileobj=urllib.request.urlopen(request))
            if items:
                return Contract.__read_item_bulk_stream__(ps)
            else:
                return Contract.__read_bid_bulk_stream__(ps)
        except urllib.error.HTTPError:
            return []

    @staticmethod
    def __read_snapshot_archive__(target_date, regions, index=None):
        """
        Read contract snapshots from archive.

        :param target_date: target date to retrieve
        :param regions: array-like of regions to retrieve
        :param index: if not None, then the contract snapshot bulk file index for this date
        :return: a map regionID -> list of (timestamp, contract list) in timestamp order.
        """
        date_string = "%04d%02d%02d" % (target_date.year, target_date.month, target_date.day)
        path_string = "%04d/%02d/%02d" % (target_date.year, target_date.month, target_date.day)
        bulk_file = "contract_snapshots_" + date_string + "_30.bulk"
        bulk_url = "https://storage.googleapis.com/evekit_md/" + path_string + "/" + bulk_file
        if index is None:
            index = Contract.__read_contract_snaps_index__(target_date)
        sorted_keys = list(index.keys())
        sorted_keys.sort()
        last_region_id = sorted_keys[-1]
        results = {}
        try:
            for next_region in regions:
                if next_region not in index.keys():
                    results[next_region] = []
                    continue
                range_string = "bytes=" + str(index[next_region][0]) + "-"
                if index[next_region][1] != -1 and next_region != last_region_id:
                    # On the last region ID, we need to leave an open range request
                    range_string += str(index[next_region][1])
                request = urllib.request.Request(bulk_url, headers={"Range": range_string})
                ps = gzip.GzipFile(fileobj=urllib.request.urlopen(request))
                results[next_region] = Contract.__read_bulk_stream__(ps, next_region)
                ps.close()
        except urllib.error.HTTPError:
            return {}
        return results

    @staticmethod
    def __get_items_or_bids__(contract_id, date, region_id, config=None, items=True):
        """
        Get the list of items or bids associated with a contract.

        :param contract_id: ID of contract for which items or bids will be retrieved
        :param date: date on which the contract existed (although may be expired)
        :param region_id: region where the contract was created
        :param config: optional configuration
        :return: a list of ContractItem/ContractBid or the empty list if the item list could not be found
        """
        config = {} if config is None else config
        use_local = config.get('use_local', False)
        if use_local:
            if items:
                return Contract.__read_local_items__(contract_id, region_id, src_dir=config.get('local_storage', None))
            else:
                return Contract.__read_local_bids__(contract_id, region_id, src_dir=config.get('local_storage', None))
        else:
            index = Contract.__read_contract_data_index__(date)
            if index == {}:
                # Failed to read index file, return empty result
                return []
            return Contract.__read_item_or_bid_archive__(date, contract_id, index=index, items=items)

    @staticmethod
    def get_contracts(date, region_id=None, config=None):
        """
        Get the set of contracts for the given date, optionally filtered by region.
        Returns a map regionID -> list of (timestamp, contract list) in timestamp order.

        :param date: date to retrieve
        :param region_id: None (all regions) or a list of regions to include
        :param config: optional configuration
        :return: a map from regionID to timestamp to contract list
        """
        config = {} if config is None else config
        use_local = config.get('use_local', False)
        if use_local:
            if region_id is None:
                raise RuntimeError("region ID list required when reading from local files")
            result = {}
            for nextRegion in region_id:
                result[nextRegion] = Contract.__read_local_snapshots__(nextRegion,
                                                                       src_dir=config.get('local_storage', None))
            return result
        else:
            index = Contract.__read_contract_snaps_index__(date)
            if index == {}:
                # Failed to read index file, return empty result
                return {}
            if region_id is None:
                region_id = list(index.keys())
            return Contract.__read_snapshot_archive__(date, region_id, index=index)


def __dline__(ps):
    next_line = ps.readline().strip()
    return next_line.decode('utf-8')
