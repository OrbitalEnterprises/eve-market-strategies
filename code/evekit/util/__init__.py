# evekit.util package
import datetime


def convert_raw_time(raw_time):
    """
    Convert time in milliseconds UTC (since the epoch) to a datetime

    :param raw_time: time in milliseconds UTC (since the epoch)
    :return: raw time converted to datetime
    """
    return datetime.datetime.fromtimestamp(raw_time//1000, datetime.timezone.utc).replace(microsecond=raw_time%1000*1000)
