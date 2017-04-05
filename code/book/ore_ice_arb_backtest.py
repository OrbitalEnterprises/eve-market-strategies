#
# Discover arb strategies for a single day.  Output results to file named on command line as CSV.
#
# Usage: python ore_ice_arb_backtest.py YYYY-MM-DD output.csv
#
import pandas as pd
import numpy as np
from pandas import DataFrame, Series
import matplotlib.pyplot as plt
import datetime
import sys
# EveKit imports
from evekit.reference import Client
from evekit.util import convert_raw_time
from evekit.marketdata import TradingUtil
from evekit.marketdata import OrderBook

# This code is a simplified version of our single day Jupyter notebook which analyzes ore and ice arbitrage
# opportunities.  A simplified version of the opportunities list is stored in CSV format in the file
# specified on the command line.  The format of each line of this file is:
#
# snapshot time, profit, gross, cost, type
#
# where:
#
# snapshot time - time when opportunity occurred in format YYYY-MM-DD HH:MM:SS
# profit - total profit for this opportunity
# gross - gross proceeds of this opportunity (less sales tax)
# cost - total cost of this opportunity (including reprocessing tax)
# type - name of source material type
#
# See the book text for more details

# Set up region, station and date range for our back test.
#
sde_client = Client.SDE.get()
region_query = "{values: ['The Forge']}"
station_query = "{values: ['Jita IV - Moon 4 - Caldari Navy Assembly Plant']}"
region_id = sde_client.Map.getRegions(regionName=region_query).result()[0][0]['regionID']
station_id = sde_client.Station.getStations(stationName=station_query).result()[0][0]['stationID']
compute_date = datetime.datetime.strptime(sys.argv[1], "%Y-%m-%d")
print("Using region_id=%d, station_id=%d on date %s" % (region_id, station_id, str(compute_date)), flush=True)

# Set up ore and ice type map
#
material_group_names = [ 'Veldspar', 'Scordite', 'Pyroxeres', 'Plagioclase', 'Omber', 'Kernite', 'Jaspet', 
                         'Hemorphite', 'Hedbergite', 'Gneiss', 'Dark Ochre', 'Spodumain', 'Crokite', 
                         'Bistot', 'Arkonor', 'Mercoxit', 'Ice' ]
group_name_query = "{values:[" + ",".join(map(lambda x : "'" + x + "'", material_group_names)) + "]}"
material_groups = Client.SDE.load_complete(sde_client.Inventory.getGroups, groupName=group_name_query)
group_id_query = "{values:[" + ",".join([str(x['groupID']) for x in material_groups]) + "]}"
source_types = {}
for next_type in Client.SDE.load_complete(sde_client.Inventory.getTypes, groupID=group_id_query):
    if next_type['marketGroupID'] is not None:
        # We perform this check because the 'Ice' family in the SDE includes some non-refinable types
        # These are detectable by the lack of a market group ID.  We create a material_map entry
        # in preparation for the next step.
        next_type['material_map'] = {}
        source_types[next_type['typeID']] = next_type

# Add in refined material information per source type
#
type_id_query = "{values:[" + ",".join([str(x) for x in source_types.keys()]) + "]}"
for next_mat in Client.SDE.load_complete(sde_client.Inventory.getTypeMaterials, typeID=type_id_query):
    source_types[next_mat['typeID']]['material_map'][next_mat['materialTypeID']] = next_mat

# Assemble the set of types we need in our order book
#
download_types = set(source_types.keys())
for next_type in source_types.values():
    download_types = download_types.union(next_type['material_map'].keys())

# Set efficiency, tax rate and station tax.

# This is the efficiency at a typical NPC station with max skills
efficiency = 0.5 * 1.15 * 1.1 * 1.1

# This is the sales tax at a typical NPC station with max skills
tax_rate = 0.01

# Station tax can be no greater than 0.05.  This value is zero if standings are 6.67 or better.
# As noted above, we're substituting order price for adjusted price.  From empirical observation,
# setting station_tax to 0.04 roughly approximates a station_tax of 0.05 with true adjusted prices.
# So we'll set station tax to 0.04 here.
station_tax = 0.04

# Function to save opportunities to a file in CSV format
#
def save_opportunities(opps, fout):
    for opp in opps:
        profit = "{:15,.2f}".format(opp['profit'])
        margin = "{:8.2f}".format(opp['margin'] * 100)
        # time, profit, gross, cost, typename
        print("%s,%s,%s,%s,%s" % (str(opp['time']), str(opp['profit']), str(opp['gross']), str(opp['cost']), opp['type']), file=fout)

# Function which attempts to buy a type from the given order list in the given volume.
# Orders in the list are "consumed" as they are used (mutates sell_order_list)
#
def attempt_buy_type_list(buy_volume, sell_order_list):
    potential = []
    for next_order in sell_order_list:
        if buy_volume >= next_order['min_volume'] and next_order['volume'] > 0:
            # Buy into this order
            amount = min(buy_volume, next_order['volume'])
            order_record = dict(price=next_order['price'], volume=amount)
            buy_volume -= amount
            next_order['volume'] -= amount
            potential.append(order_record)
        if buy_volume == 0:
            # We've completely filled this order
            return potential
    # If we never completely fill the order then return no orders
    return []


# Function which attempts to sell a type to the given order list in the given volume.
# Orders in the list are "consumed" as they are used (mutates buy_order_list)
# Set use_citadel=True to resolve citadel locations for more accurate order matching.
#
def attempt_sell_type_list(sell_region_id, sell_location_id, sell_volume, buy_order_list):
    config = dict(use_citadel=False)
    potential = []
    for next_order in buy_order_list:
        try:
            if sell_volume >= next_order['min_volume'] and next_order['volume'] > 0 and \
               TradingUtil.check_range(sell_region_id, sell_location_id, next_order['location_id'], 
                                       next_order['order_range'], config):
                # Sell into this order
                amount = min(sell_volume, next_order['volume'])
                order_record = dict(price=next_order['price'], volume=amount)
                sell_volume -= amount
                next_order['volume'] -= amount
                potential.append(order_record)
        except:
            # We'll get an exception if TradingUtil can't find the location of a player-owned
            # station.  We'll ignore those for now.  Change "use_citadeL" to True above
            # if you'd like to attempt to resolve the location of these stations from a 
            # third party source.
            pass
        if sell_volume == 0:
            # We've completely filled this order
            return potential
    # If we never completely fill the order then return no orders
    return []

# Function to extract sell orders for the given type at the given station ID
# from the given order book snapshot.
#
def extract_sell_orders(snapshot, type_id, station_id):
    by_type = snapshot[snapshot.type_id == type_id]
    by_loc = by_type[by_type.location_id == station_id]
    by_side = by_loc[by_loc.buy == False]
    return [next_order[1] for next_order in by_side.iterrows()]

# Function extract buy orders for the given type from the given order book
# snapshot.
#
def extract_buy_orders(snapshot, type_id):
    by_type = snapshot[snapshot.type_id == type_id]
    by_side = by_type[by_type.buy == True]
    return [next_order[1] for next_order in by_side.iterrows()]

# Function to combine orders of the same type by price so that the
# resulting list has one entry for each price, with the total volume
# filled at that price.
#
def compress_order_list(order_list, ascending=True):
    order_map = {}
    for next_order in order_list:
        if next_order['price'] not in order_map:
            order_map[next_order['price']] = next_order['volume']
        else:
            order_map[next_order['price']] += next_order['volume']
    orders = [ dict(price=k,volume=v) for k, v in order_map.items()]
    return sorted(orders, key=lambda x: x['price'], reverse=not ascending)

# Function which attempts to consume all opportunities for a single type in a given snapshot.
# This function will attempt to buy and refine as long as it is profitable to do so.
# The result of this function will be None if no opportunity was available, or an object:
#
# {
#   gross: gross proceeds (total of all sales)
#   cost: total cost (cost of buying source plus refinement costs)
#   profit: gross - cost
#   margin: cost / profit
#   buy_orders: the compressed list of buy orders that were placed
#   sell_orders: map from material type ID to the compressed list of sell orders that were placed
# }
#
# Compressed order lists group orders by price and sum the volume.
#
def attempt_opportunity(snapshot, type_id, region_id, station_id, type_map, tax_rate, efficiency, station_tax):
    # Reduce to type to extract minimum reprocessing volume
    by_type = snapshot[snapshot.type_id == type_id]
    required_volume = type_map[type_id]['portionSize']
    #
    # Create source sell order list.
    sell_order_list = extract_sell_orders(snapshot, type_id, station_id)
    #
    # Create refined materials buy order lists.
    buy_order_map = {}
    all_sell_orders = {}
    for next_mat in type_map[type_id]['material_map'].values():
        mat_type_id = next_mat['materialTypeID']
        buy_order_map[mat_type_id] = extract_buy_orders(snapshot, mat_type_id)
        all_sell_orders[mat_type_id] = []
    #
    # Now iterate through sell orders until we stop making a profit
    all_buy_orders = []
    gross = 0
    cost = 0
    while True:
        #
        # Attempt to buy source material
        current_cost = 0
        current_gross = 0
        bought = attempt_buy_type_list(required_volume, sell_order_list)
        if len(bought) == 0:
            # Can't buy any more source material, done with this opportunity
            break
        #
        # Add cost of buying source material
        current_cost = np.sum([ x['price'] * x['volume'] for x in bought ])
        #
        # Now attempt to refine and sell all refined materials
        sell_orders = {}
        for next_mat_id in buy_order_map.keys():
            sell_volume = int(type_map[type_id]['material_map'][next_mat_id]['quantity'] * efficiency)
            sold = attempt_sell_type_list(region_id, station_id, sell_volume, buy_order_map[next_mat_id])
            if len(sold) == 0:
                # Can't sell any more refined material, done with this opportunity
                sell_orders = []
                break
            #
            # Add gross profit from selling refined material
            current_gross += (1 - tax_rate) * np.sum([ x['price'] * x['volume'] for x in sold ])
            #
            # Add incremental cost of refining source to this refined material.
            # If we had actual adjusted_prices, we'd use those prices in place of x['price'] below.
            current_cost += station_tax * np.sum([ x['price'] * x['volume'] for x in sold ])
            #
            # Save the set of sale orders we just made
            sell_orders[next_mat_id] = sold
        #
        if len(sell_orders) == 0:
            # We couldn't sell all refined material, so we're done with this opportunity
            break
        #
        # Check whether we've made a profit this round.  If so, record the amounts and continue
        if current_gross > current_cost:
            all_buy_orders.extend(bought)
            for i in sell_orders.keys():
                all_sell_orders[i].extend(sell_orders[i])
            cost += current_cost
            gross += current_gross
        else:
            # This round didn't make any profit so we're done with this opportunity
            break
    #
    # If we were able to make any profit, then report the opportunity
    if gross > cost:
        for i in all_sell_orders.keys():
            all_sell_orders[i]=compress_order_list(all_sell_orders[i], False)
        return dict(gross=gross, cost=cost, profit=gross - cost, margin=(gross - cost)/cost, 
                    buy_orders=compress_order_list(all_buy_orders), 
                    sell_orders=all_sell_orders)
    return None

# Function which finds all opportunities in the given order book for all ore and ice
# types in the given type map.  Source materials are assumed to be purchased at the given
# station.  Refined materials are assumed to be sold from the given station ID into the
# given region ID.  The remaining parameters configure the reprocessing equation.
#
def find_opportunities(order_book, type_map, station_id, region_id, efficiency, sales_tax, station_tax, verbose=False):
    total_snapshots = len(order_book.groupby(order_book.index))
    if verbose:
        print("Checking %d snapshots for opportunities" % total_snapshots, flush=True)
    opportunities = []
    count = 0
    for snapshot_group in order_book.groupby(order_book.index):
        #
        # Each group is a pair (snapshot_time, snapshot_dataframe)
        snapshot_time = snapshot_group[0]
        snapshot = snapshot_group[1]
        if verbose:
            print("X", end='', flush=True)
            count += 1
            if count % 72 == 0:
                print()
        #
        # Iterate through each source type looking for opportunities
        for source_type in type_map.values():
            opp = attempt_opportunity(snapshot, source_type['typeID'], region_id, station_id, type_map, 
                                      sales_tax, efficiency, station_tax)
            if opp is not None:
                #
                # Save the time and type if we've found a valid opportunity
                opp['time'] = snapshot_time
                opp['type'] = source_type['typeName']
                opportunities.append(opp)
    if verbose:
        print(flush=True)
    return opportunities


# Load the order book for the target day
order_book = OrderBook.get_data_frame(dates=[compute_date], types=download_types, regions=[region_id], 
                                      config=dict(local_storage=".", tree=True, skip_missing=True, 
                                                  use_online=False, verbose=True))
    
# Find opportunities
all_opportunities = find_opportunities(order_book, source_types, station_id, region_id, 
                                       efficiency, tax_rate, station_tax, verbose=True)

# Write raw opps out to disk
fout = open(sys.argv[2], 'w')
save_opportunities(all_opportunities, fout)
fout.close()
