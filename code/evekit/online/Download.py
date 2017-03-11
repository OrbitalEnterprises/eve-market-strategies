# evekit.online.Downloader module
import urllib.request
import urllib.error
import os


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
        skip_missing - if True, skip missing data.  Otherwise, throw an exception on unfound data.
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


