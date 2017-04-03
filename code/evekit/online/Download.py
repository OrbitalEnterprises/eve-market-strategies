# evekit.online.Downloader module
import urllib.request
import urllib.error
import os
import gzip
import shutil


def __download_market_history__(target_date, parent_dir):
    """
    Download market history file for the given date to the given location

    :param target_date: datetime for which history will be downloaded
    :param parent_dir: directory where downloads will be stored
    :return: None
    """
    path_string = "%04d/%02d/%02d" % (target_date.year, target_date.month, target_date.day)
    name_string = "%04d%02d%02d" % (target_date.year, target_date.month, target_date.day)
    bulk_file = "market_" + name_string + ".bulk"
    index_file = "market_" + name_string + ".index.gz"
    bulk_url = "https://storage.googleapis.com/evekit_md/" + path_string + "/" + bulk_file
    index_url = "https://storage.googleapis.com/evekit_md/" + path_string + "/" + index_file
    urllib.request.urlretrieve(bulk_url, parent_dir + "/" + bulk_file)
    urllib.request.urlretrieve(index_url, parent_dir + "/" + index_file)


def download_market_history_range(date_range, parent_dir, config=None):
    """
    Download market history files for a date range

    :param date_range: array like of datetime for which data will be downloaded
    :param parent_dir: directory where dates will be stored
    :param config: optional configuration parameters:
        verbose - if True, display what we're doing
        tree - if True, store downloads in a tree of directories, e.g. parent_dir/YYYY/MM/DD/...
        skip_missing - if True, skip missing data.  Otherwise, throw an exception on missing data.
    :return: None
    """
    config = {} if config is None else config
    verbose = config.get('verbose', False)
    tree = config.get('tree', False)
    skip_missing = config.get('skip_missing', True)
    for next_date in date_range:
        if verbose:
            print("Downloading " + str(next_date), end="...")
        try:
            target_dir = parent_dir
            if tree:
                path_string = "%04d/%02d/%02d" % (next_date.year, next_date.month, next_date.day)
                target_dir = parent_dir + "/" + path_string
                os.makedirs(target_dir, exist_ok=True)
            __download_market_history__(next_date, target_dir)
            if verbose:
                print("done")
        except (urllib.error.HTTPError, OSError) as e:
            if verbose:
                print("missing")
            if not skip_missing:
                raise Exception("Failed to download date: " + str(next_date)) from e


def __get_order_book_index__(fobj, max_offset):
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


def __download_order_book__(target_date, parent_dir, types=None, regions=None):
    """
    Download order book file for the given date to the given location, optionally filtered by types and regions.
    Note that the index file is NOT downloaded if the bulk file is filtered.

    :param target_date: datetime for which order book will be downloaded
    :param parent_dir: directory where downloads will be stored
    :param types: array-like of types to download.  Files will be filtered to only include the specified types.
                  If None, then download all types.
    :param regions: array-like of regions to download.  Files will be filtered to only include the specified regions.
                    If None, then download all regions.
    :return: None
    """
    path_string = "%04d/%02d/%02d" % (target_date.year, target_date.month, target_date.day)
    name_string = "%04d%02d%02d" % (target_date.year, target_date.month, target_date.day)
    bulk_file = "interval_" + name_string + "_5.bulk"
    index_file = "interval_" + name_string + "_5.index.gz"
    bulk_url = "https://storage.googleapis.com/evekit_md/" + path_string + "/" + bulk_file
    index_url = "https://storage.googleapis.com/evekit_md/" + path_string + "/" + index_file
    # If not filtered, then download everything
    if types is None and regions is None:
        urllib.request.urlretrieve(bulk_url, parent_dir + "/" + bulk_file)
        urllib.request.urlretrieve(index_url, parent_dir + "/" + index_file)
        return
    # Clean out any tmp files from before
    tmp_file_prefix = bulk_file + "._tmp_."
    for ff in os.listdir(parent_dir):
        if ff.startswith(tmp_file_prefix):
            os.remove(parent_dir + '/' + ff)
    # If filtered, then filter through by type and region
    # Note that we need to reconstruct the index file locally so we write temporary files first, then
    # concatenate and rebuild the index file locally.
    index_map = __get_order_book_index__(urllib.request.urlopen(index_url), -1)
    for next_type in index_map.keys():
        if types is not None and next_type not in types:
            # Skip types we don't care about
            continue
        next_tmp_file = parent_dir + "/" + tmp_file_prefix + str(next_type) + ".gz"
        next_out = gzip.open(next_tmp_file, 'wb')
        range_string = "bytes=" + str(index_map[next_type][0]) + "-"
        if index_map[next_type][1] != -1:
            range_string += str(index_map[next_type][1])
        request = urllib.request.Request(bulk_url, headers={"Range": range_string})
        type_id = None
        snap_count = None
        snap_countdown = 0
        region_id = None
        snap_time = None
        buy_count = None
        sell_count = None
        seen_regions = []
        for line in gzip.GzipFile(fileobj=urllib.request.urlopen(request)).readlines():
            line = line.decode('utf-8')
            if type_id is None:
                type_id = int(line.strip())
                next_out.write((str(type_id) + "\n").encode('utf-8'))
                continue
            if snap_count is None:
                snap_count = int(line.strip())
                next_out.write((str(snap_count) + "\n").encode('utf-8'))
                continue
            if region_id is None:
                region_id = int(line.strip())
                if regions is not None and region_id not in regions:
                    # Indicate we're skipping this region
                    region_id = -region_id
                else:
                    # We're including this region
                    seen_regions.append(region_id)
                    next_out.write((str(region_id) + "\n").encode('utf-8'))
                snap_countdown = snap_count
                continue
            if snap_time is None:
                snap_time = int(line.strip())
                if region_id > 0:
                    next_out.write((str(snap_time) + "\n").encode('utf-8'))
                continue
            if buy_count is None:
                buy_count = int(line.strip())
                if region_id > 0:
                    next_out.write((str(buy_count) + "\n").encode('utf-8'))
                continue
            if sell_count is None:
                sell_count = int(line.strip())
                if region_id > 0:
                    next_out.write((str(sell_count) + "\n").encode('utf-8'))
                order_count = buy_count + sell_count
                if order_count > 0:
                    # At least one order to read, proceed.  Otherwise, we'll fall through to the
                    # zero order count check.
                    continue
            if order_count > 0:
                if region_id > 0:
                    next_out.write((line.strip() + "\n").encode('utf-8'))
                order_count -= 1
                # Fallthrough to check whether this was the last order for this snap
            if order_count == 0:
                # Reset for next snapshot
                snap_time = None
                buy_count = None
                sell_count = None
                snap_countdown -= 1
                # Fallthrough to check whether this was the last snap for this region
            else:
                # More orders to read, fetch next
                continue
            if snap_countdown == 0:
                # Reset for next region
                region_id = None
                if regions is not None and len(seen_regions) == len(regions):
                    # Short circuit since we've seen all the regions we care about
                    break
        # Finished with current file
        next_out.close()
    # Concatenate files into a new bulk file and build a new index file
    next_offset = 0
    new_bulk_file = parent_dir + "/" + bulk_file
    new_index_file = parent_dir + "/" + index_file
    bulk_file_out = open(new_bulk_file, 'wb')
    index_file_out = gzip.open(new_index_file, 'wb')
    for ff in os.listdir(parent_dir):
        if ff.startswith(tmp_file_prefix):
            # Determine type ID from file name
            file_size = os.stat(parent_dir + '/' + ff).st_size
            type_id = ff[ff[:-3].rindex('.') + 1:-3]
            # Concatenate file to new bulk file
            next_file = open(parent_dir + '/' + ff, 'rb')
            shutil.copyfileobj(next_file, bulk_file_out)
            next_file.close()
            # Write index entry for this file
            entry_name = 'interval_' + str(type_id) + '_' + name_string + '_5.book.gz'
            index_file_out.write((entry_name + " " + str(next_offset) + "\n").encode('utf-8'))
            next_offset += file_size
            # Delete file once we've added it
            os.remove(parent_dir + '/' + ff)
    bulk_file_out.close()
    index_file_out.close()


def download_order_book_range(date_range, parent_dir, types=None, regions=None, config=None):
    """
    Download order book files for a date range, optionally filtered to the given types and regions.

    :param date_range: array like of datetime for which data will be downloaded
    :param parent_dir: directory where dates will be stored
    :param types: array-like of types to download.  Files will be filtered to only include the specified types.
                  If None, then download all types.
    :param regions: array-like of regions to download.  Files will be filtered to only include the specified regions.
                    If None, then download all regions.
    :param config: optional configuration parameters:
        verbose - if True, display what we're doing
        tree - if True, store downloads in a tree of directories, e.g. parent_dir/YYYY/MM/DD/...
        skip_missing - if True, skip missing data.  Otherwise, throw an exception on missing data.
    :return: None
    """
    config = {} if config is None else config
    verbose = config.get('verbose', False)
    tree = config.get('tree', False)
    skip_missing = config.get('skip_missing', True)
    for next_date in date_range:
        if verbose:
            print("Downloading " + str(next_date), end="...")
        try:
            target_dir = parent_dir
            if tree:
                path_string = "%04d/%02d/%02d" % (next_date.year, next_date.month, next_date.day)
                target_dir = parent_dir + "/" + path_string
                os.makedirs(target_dir, exist_ok=True)
            __download_order_book__(next_date, target_dir, types, regions)
            if verbose:
                print("done")
        except (urllib.error.HTTPError, OSError) as e:
            if verbose:
                print("missing")
            if not skip_missing:
                raise Exception("Failed to download date: " + str(next_date)) from e
