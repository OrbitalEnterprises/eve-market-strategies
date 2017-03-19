# evekit.map.Region module
"""
Retrieve map information for EVE regions
"""
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import shortest_path
from evekit.reference import Client


class Station:
    def __init__(self, station_id, region_id, json=None):
        self.station_id = station_id
        self.region_id = region_id
        if json is None:
            sde_client = Client.SDE.get()
            query_string = "{values: [" + str(station_id) + "]}"
            json, status = sde_client.Station.getStations(station_id=query_string).result()
            if status.status_code != 200 or len(json) == 0:
                raise Exception("Unable to resolve station ID: %d" % station_id)
            json = json[0]
        self.security = float(json['security'])
        self.docking_cost_per_volume = float(json['dockingCostPerVolume'])
        self.max_ship_volume_dockable = float(json['maxShipVolumeDockable'])
        self.office_rental_cost = float(json['officeRentalCost'])
        self.operation_id = int(json['operationID'])
        self.station_type_id = int(json['stationTypeID'])
        self.corporation_id = int(json['corporationID'])
        self.solar_system_id = int(json['solarSystemID'])
        self.constellation_id = int(json['constellationID'])
        self.region_name = json['stationName']
        self.x = float(json['x'])
        self.y = float(json['y'])
        self.z = float(json['z'])
        self.reprocessing_efficiency = float(json['reprocessingEfficiency'])
        self.reprocessing_stations_take = float(json['reprocessingStationsTake'])
        self.reprocessing_hangar_flag = int(json['reprocessingHangarFlag'])


class SolarSystem:
    def __init__(self, solar_system_id, region_id, json=None):
        self.solar_system_id = solar_system_id
        self.region_id = region_id
        self.neighbors = []
        if json is None:
            sde_client = Client.SDE.get()
            query_string = "{values: [" + str(solar_system_id) + "]}"
            json, status = sde_client.Map.getSolarSystems(solar_system_id=query_string).result()
            if status.status_code != 200 or len(json) == 0:
                raise Exception("Unable to resolve solar system ID: %d" % solar_system_id)
            json = json[0]
        self.constellation_id = int(json['constellationID'])
        self.solar_system_name = json['solarSystemName']
        self.x = float(json['x'])
        self.y = float(json['y'])
        self.z = float(json['z'])
        self.luminosity = float(json['luminosity'])
        self.border = int(json['border']) == 1
        self.fringe = int(json['fringe']) == 1
        self.corridor = int(json['corridor']) == 1
        self.hub = int(json['hub']) == 1
        self.international = int(json['international']) == 1
        self.region = int(json['regional']) == 1
        self.security = float(json['security'])
        self.faction_id = int(json['factionID'])
        self.radius = float(json['radius'])
        self.sun_type_id = int(json['sunTypeID'])
        self.security_class = json['securityClass']
        self.xmax = float(json['xmax'])
        self.xmin = float(json['xmin'])
        self.ymax = float(json['ymax'])
        self.ymin = float(json['ymin'])
        self.zmax = float(json['zmax'])
        self.zmin = float(json['zmin'])

    def add_neighbor(self, neighbor_solar_id):
        if neighbor_solar_id not in self.neighbors:
            self.neighbors.append(neighbor_solar_id)


class Constellation:
    def __init__(self, constellation_id, region_id, json=None):
        self.constellation_id = constellation_id
        self.region_id = region_id
        self.neighbors = []
        if json is None:
            sde_client = Client.SDE.get()
            query_string = "{values: [" + str(constellation_id) + "]}"
            json, status = sde_client.Map.getConstellations(constellation_id=query_string).result()
            if status.status_code != 200 or len(json) == 0:
                raise Exception("Unable to resolve constellation ID: %d" % constellation_id)
            json = json[0]
        self.constellation_name = json['constellationName']
        self.x = float(json['x'])
        self.y = float(json['y'])
        self.z = float(json['z'])
        self.faction_id = int(json['factionID'])
        self.radius = float(json['radius'])
        self.xmax = float(json['xmax'])
        self.xmin = float(json['xmin'])
        self.ymax = float(json['ymax'])
        self.ymin = float(json['ymin'])
        self.zmax = float(json['zmax'])
        self.zmin = float(json['zmin'])

    def add_neighbor(self, neighbor_const_id):
        if neighbor_const_id not in self.neighbors:
            self.neighbors.append(neighbor_const_id)


__region_cache__ = {}


class Region:
    @staticmethod
    def get_region(region_id):
        if region_id in __region_cache__:
            return __region_cache__[region_id]
        obj = Region(region_id)
        __region_cache__[region_id] = obj
        return obj

    def __init__(self, region_id, json=None):
        self.region_id = region_id
        # If no initialization provided, then lookup information
        if json is None:
            sde_client = Client.SDE.get()
            region_info, status = sde_client.Map.getRegions(regionID="{values: [" + str(region_id) + "]}").result()
            if status.status_code != 200 or len(region_info) == 0:
                raise Exception("Unable to resolve region ID: %d" % region_id)
            json = region_info[0]
        self.region_name = json['regionName']
        self.x = float(json['x'])
        self.y = float(json['y'])
        self.z = float(json['z'])
        self.faction_id = int(json['factionID'])
        self.x_max = float(json['xmax'])
        self.x_min = float(json['xmin'])
        self.y_max = float(json['ymax'])
        self.y_min = float(json['ymin'])
        self.z_max = float(json['zmax'])
        self.z_min = float(json['zmin'])
        # Cache constellations, solar systems and stations
        self.__load_constellations__()
        self.__load_solar_systems__()
        self.__load_stations__()
        self.__build_adjacencies__()
        self.__build_shortest_path__()

    @staticmethod
    def __batch_load__(query_func):
        result = []
        cont_id = 0
        sde_client = Client.SDE.get()
        batch, status = query_func(cont_id, sde_client)
        while status.status_code == 200 and len(batch) > 0:
            result.extend(batch)
            cont_id += len(batch)
            batch, status = query_func(cont_id, sde_client)
        return result

    def __load_constellations__(self, json=None, neighbor_json=None):
        # Load constellations
        self.constellation_map = {}
        self.constellation_index = {}
        if json is None:
            query_string = "{values: [" + str(self.region_id) + "]}"
            rtr = lambda cont, client: client.Map.getConstellations(contid=cont, regionID=query_string).result()
            json = Region.__batch_load__(rtr)
        count = 0
        for next_const in json:
            const_id = next_const['constellationID']
            obj = Constellation(constellation_id=const_id, region_id=self.region_id, json=next_const)
            obj.index = count
            self.constellation_map[const_id] = obj
            self.constellation_index[count] = const_id
            count += 1
        # Load constellation neighbor relationships
        if neighbor_json is None:
            query_string = "{values: [" + str(self.region_id) + "]}"
            rtr = lambda cont, client: client.Map.getConstellationJumps(contid=cont, fromRegionID=query_string,
                                                                        toRegionID=query_string).result()
            neighbor_json = Region.__batch_load__(rtr)
        for next_jump in neighbor_json:
            from_id = next_jump['fromConstellationID']
            to_id = next_jump['toConstellationID']
            self.constellation_map[from_id].add_neighbor(to_id)
            self.constellation_map[to_id].add_neighbor(from_id)

    def __load_solar_systems__(self, json=None, neighbor_json=None):
        # Load solar systems
        self.solar_system_map = {}
        self.solar_system_index = {}
        if json is None:
            query_string = "{values: [" + str(self.region_id) + "]}"
            rtr = lambda cont, client: client.Map.getSolarSystems(contid=cont, regionID=query_string).result()
            json = Region.__batch_load__(rtr)
        count = 0
        for next_solar in json:
            solar_id = next_solar['solarSystemID']
            obj = SolarSystem(solar_system_id=solar_id, region_id=self.region_id, json=next_solar)
            obj.index = count
            self.solar_system_map[solar_id] = obj
            self.solar_system_index[count] = solar_id
            count += 1
        # Load solar system neighbor relationships
        if neighbor_json is None:
            query_string = "{values: [" + str(self.region_id) + "]}"
            rtr = lambda cont, client: client.Map.getSolarSystemJumps(contid=cont, fromRegionID=query_string,
                                                                      toRegionID=query_string).result()
            neighbor_json = Region.__batch_load__(rtr)
        for next_jump in neighbor_json:
            from_id = next_jump['fromSolarSystemID']
            to_id = next_jump['toSolarSystemID']
            self.solar_system_map[from_id].add_neighbor(to_id)
            self.solar_system_map[to_id].add_neighbor(from_id)

    def __load_stations__(self, json=None):
        # Load stations
        self.station_map = {}
        if json is None:
            query_string = "{values: [" + str(self.region_id) + "]}"
            rtr = lambda cont, client: client.Station.getStations(contid=cont, regionID=query_string).result()
            json = Region.__batch_load__(rtr)
        for next_station in json:
            station_id = next_station['stationID']
            obj = Station(station_id=station_id, region_id=self.region_id, json=next_station)
            self.station_map[station_id] = obj

    def __build_adjacencies__(self):
        # Construct constellation adjacency matrix
        mat_count = len(self.constellation_index)
        adj_array = []
        for i in range(mat_count):
            next_row = []
            source_const = self.constellation_index[i]
            for j in range(mat_count):
                dest_const = self.constellation_index[j]
                if dest_const in self.constellation_map[source_const].neighbors:
                    next_row.append(1)
                else:
                    next_row.append(0)
            adj_array.append(next_row)
        self.constellation_adj_matrix = csr_matrix(adj_array)
        # Construct solar system adjacency matrix
        mat_count = len(self.solar_system_index)
        adj_array = []
        for i in range(mat_count):
            next_row = []
            source_solar = self.solar_system_index[i]
            for j in range(mat_count):
                dest_solar = self.solar_system_index[j]
                if dest_solar in self.solar_system_map[source_solar].neighbors:
                    next_row.append(1)
                else:
                    next_row.append(0)
            adj_array.append(next_row)
        self.solar_system_adj_matrix = csr_matrix(adj_array)

    def __build_shortest_path__(self):
        self.constellation_shortest_matrix = shortest_path(self.constellation_adj_matrix, directed=False,
                                                           return_predecessors=False, unweighted=True)
        self.solar_system_shortest_matrix = shortest_path(self.solar_system_adj_matrix, directed=False,
                                                          return_predecessors=False, unweighted=True)

    def constellation_jump_count(self, from_const_id, to_const_id):
        if from_const_id not in self.constellation_map.keys() or to_const_id not in self.constellation_map.keys():
            return None
        from_index = self.constellation_map[from_const_id].index
        to_index = self.constellation_map[to_const_id].index
        return self.constellation_shortest_matrix[from_index][to_index]

    def solar_system_jump_count(self, from_solar_id, to_solar_id):
        if from_solar_id not in self.solar_system_map.keys() or to_solar_id not in self.solar_system_map.keys():
            return None
        from_index = self.solar_system_map[from_solar_id].index
        to_index = self.solar_system_map[to_solar_id].index
        return self.solar_system_shortest_matrix[from_index][to_index]
