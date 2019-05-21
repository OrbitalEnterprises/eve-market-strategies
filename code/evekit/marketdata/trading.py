# evekit.marketdata.TradingUtil module
"""
Various utilities for trading computations
"""
from evekit.map import Region
from evekit.reference import Client


class TradingUtil:
    def __init__(self):
        pass

    @staticmethod
    def resolve_solar_system(region_id, station_id):
        region_info = Region.get_region(region_id)
        if station_id in region_info.station_map.keys():
            return region_info.station_map[station_id].solar_system_id
        return None

    @staticmethod
    def order_match(region_id, solar_system_id, station_id, order):
        """
        Check whether a sell order placed at the given station in the given solar system could
        be matched by the target order.

        :param region_id: region where sell order will be placed
        :param solar_system_id: solar system where sell order will be placed
        :param station_id: station where sell order will be placed
        :param order: order information
        :return:
        """
        # Case 1 - order has range "region"
        if str(order.order_range) == 'region':
            return True
        # Case 2 - order has range "station" and is in the same location
        if str(order.order_range) == 'station':
            return order.location_id == station_id
        # Case 3 - order has range "solarsystem" and has location in the same solar system as stationID
        region_info = Region.get_region(region_id)
        if str(order.order_range) == 'solarsystem':
            return order.location_id in region_info.station_map.keys() and \
                   region_info.station_map[order.location_id].solar_system_id == solar_system_id
        # Case 4 - order has a jump range and stationID is within the listed jump range
        if order.system_id in region_info.solar_system_map.keys():
            return region_info.solar_system_jump_count(solar_system_id, order.system_id) <= int(order.orderRange)
        return False

    @staticmethod
    def check_range(region_id, sell_station_id, buy_station_id, order_range):
        """
        Check whether a sell order in the given selling station is within range of a buy
        order in the given buying station where the buying order has the given
        order range.

        :param region_id: region ID where stations are located
        :param sell_station_id: station ID where the sell order wil be placed
        :param buy_station_id: station ID where the buy order resides
        :param order_range: order range for the buy order
        :return: None if solar system information was required but could not be resolved,
          otherwise returns True if the sell order is within range of the buy order, and
          False otherwise.
        """
        # Case 1 - "region"
        if order_range == 'region':
            return True
        # Case 2 - "station"
        if order_range == 'station':
            return sell_station_id == buy_station_id
        # Remaining checks require solar system IDs and distance between solar systems
        sell_solar = TradingUtil.resolve_solar_system(region_id, sell_station_id)
        buy_solar = TradingUtil.resolve_solar_system(region_id, buy_station_id)
        # Make sure we actually found solar systems before continuing.
        # We'll return False if we can't find both solar systems.
        if sell_solar is None or buy_solar is None:
            if sell_solar is None:
                raise Exception("Missing solar system for sell station: %d" % sell_station_id)
            if buy_solar is None:
                raise Exception("Missing solar system for buy station: %d" % buy_station_id)
            return False
        #
        # Case 3 - "solarsystem"
        if order_range == 'solarsystem':
            return sell_solar == buy_solar
        # Case 4 - check jump range between solar systems
        region_info = Region.get_region(region_id)
        jump_count = region_info.solar_system_jump_count(sell_solar, buy_solar)
        return jump_count <= int(order_range)
