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
    def resolve_solar_system(region_id, station_id, citadel_client=None, esip_client=None):
        region_info = Region.get_region(region_id)
        if station_id in region_info.station_map.keys():
            return region_info.station_map[station_id].solar_system_id
        if esip_client is not None:
            result, status = esip_client.Universe.get_universe_structures_structure_id(structure_id=station_id).result()
            if status.status_code == 200 and len(result) > 0:
                return result[0]['solar_system_id'];
        if citadel_client is not None:
            result, status = citadel_client.Citadel.getCitadel(citadel_id=station_id).result()
            if status.status_code == 200 and str(station_id) in result:
                return result[str(station_id)]['systemId']
        return None

    @staticmethod
    def check_range(region_id, sell_station_id, buy_station_id, order_range, config=None):
        """
        Check whether a sell order in the given selling station is within range of a buy
        order in the given buying station where the buying order has the given
        order range.

        :param region_id: region ID where stations are located
        :param sell_station_id: station ID where the sell order wil be placed
        :param buy_station_id: station ID where the buy order resides
        :param order_range: order range for the buy order
        :param config: an optional configuration dictionary with settings:
          use_citadel - if True, resolve player-owned structure information using the Citadel client
          use_esi_proxy - if True, resolve player-owned structure information using the ESI Proxy client
          esip_key - ESI Proxy key (required if use_esi_proxy is True)
          esip_hash - ESI Proxy hash (required if use_esi_proxy is True)
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
        config = {} if config is None else config
        use_citadel = config.get('use_citadel', False)
        use_esi_proxy = config.get('use_esi_proxy', False)
        citadel_client = None
        esip_client = None
        if use_citadel:
            citadel_client = Client.Citadel.get()
        if use_esi_proxy:
            esip_key = config.get('esip_key', None)
            esip_hash = config.get('esip_hash', None)
            if esip_key is None or esip_hash is None:
                raise Exception("ESI Proxy option requires key and hash")
            esip_client = Client.ESIProxy.get(esip_key, esip_hash)
        sell_solar = TradingUtil.resolve_solar_system(region_id, sell_station_id, citadel_client, esip_client)
        buy_solar = TradingUtil.resolve_solar_system(region_id, buy_station_id, citadel_client, esip_client)
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
