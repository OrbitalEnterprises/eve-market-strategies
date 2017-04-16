# Arbitrage

In real-world markets, arbitrage is the process of simultaneously purchasing and selling an asset \(or similar assets\) in different markets.  An arbitrage trade exploits price differences between the same asset in different markets, or between an asset and related assets in the same market.  Such differences occur because of market inefficiencies.  That is, when the price of an asset deviates from *fair market value*, which is the price at which "reasonably knowledgeable" investors are willing to trade an asset.  A "reasonably knowledgeable" investor is assumed to be implicitly aware of all the factors which influence an asset's price, which are then incorporated to select a fair price for trade.  Trading strategies we'll discuss in later chapters derive their profit from these price deviations and their eventual correction.  Price correction, however, is not required for arbitrage.  In fact, arbitrage strategies only profit while price discrepancies exist.  Can we ever be sure price discrepancies *do* exist?  Generally speaking, we don't know that this will ever be the case.  In particular, subscribers to the [Efficient-Market Hypothesis](https://en.wikipedia.org/wiki/Efficient-market_hypothesis), which states that asset prices always \(eventually\) converge to fair market value, might say that price discrepancies are either non-existent or too rare to be profitable in a modern market.  In EVE, however, we'll show that these opportunities do exist and make a respectable profit.

In EVE markets, an arbitrage trade of the same asset in different markets is not possible without hauling[^10].  Instead, arbitrage opportunities in EVE are based on assets which can be refined or reprocessed into related assets which are also sold on the market.  This type of arbitrage is similar to [Index Arbitrage](https://en.wikipedia.org/wiki/Index_arbitrage) in real-world markets.  For example, raw ores like Veldspar can be traded on the market.  But Veldspar can also be refined into Tritanium which can *also* be traded on the market.  Therefore, the fair market value of Veldspar is dependent on the price of Tritanium.  If the price of Veldspar deviates far enough below fair market value, it may become profitable to buy Veldspar, refine it to Tritanium, and sell the Tritanium.  This is the essence of the trading strategies we discuss in this chapter.

The rest of this chapter will explore arbitrage opportunities in EVE.  Impatient readers may wonder whether their time is well spent on this strategy.  Are arbitrage opportunities profitable?  If so, how much?  We won't make a habit of this, but let's take a look at performance we've been able to achieve here at Orbital Enterprises.  The following graph shows performance of our arbitrage based strategy from November 2016 through March 2017:

![Performance of an Actual Arbitrage Strategy](img/ch2_fig1.PNG)

We seeded our portfolio with 2B ISK, then executed our arbitrage strategy across the five main trading regions of EVE using only our starting balance.  We use three EVE characters to conduct our trading, placed strategically in the most active markets.  As of this writing, our balance is over 38B ISK for a profit of over 36B ISK in just under five months, or an average of about 7B ISK/month.  We haven't run the strategy long enough to uncover any seasonal effects, but it's clear late fall was more profitable than more recent returns.  We currently estimate a comfortable run rate of at least 3B ISK/month.  Compared to typical real-world market strategies, these returns are outstanding.

## What Makes Arbitrage Possible?

Before we get too far into analyzing arbitrage opportunities, it is worth briefly discussing why arbitrage is possible at all.  At its root, arbitrage is made possible by one or both of the following market behaviors:

1. when the ask price of a source material falls below fair market value price as determined by the reprocessing equation \(see below\); and/or,
2. when the bid price of one or more refined materials rises above fair market value price as determined by the reprocessing equation.

There are many reasons why prices may move.  Given our knowledge of EVE player behavior, we know that some players regularly dispose of unwanted assets at cheap prices on the market.  We also know that some players focused on mining choose to trade raw ores directly as they may lack the skills to make trading refined materials possible.  Finally, we know that there are regular spikes in refined material prices as these materials are used to build the favored assets needed for wars and general PvP.

The fact that arbitrage depends on market price moves means it is possible in some cases to actually *predict* when good opportunities will occur.  We discuss once such strategy [below](#capture-dumping-with-buy-orders).  More generally, any price forecast algorithm has the potential to be used to predict arbitrage opportunities.

## Ore and Ice Refinement Arbitrage

We first consider arbitrage on ore and ice.  These asset types are organized into families of which there are six variants for each family.  The first three variants differ in refining yield and output \(for ice\).  The second three variants are "compressed" versions of the first three in which the same yield and output is achieved from a smaller volume of raw material.  There are currently sixteen ore families and four ice families, giving a total of 120 variants which can be refined into minerals and other raw materials.  An arbitrage opportunity exists if a variant can be purchased at a low enough price such that refining and selling the refined materials yields a profit.

We won't describe ore and ice refinement in detail here.  We refer interested readers to the [Reprocessing page](https://wiki.eveuniversity.org/Reprocessing) at EVE University[^11]. For our discussion, it suffices to know that each ore or ice variant has an "ideal" refining output which is adjusted by the efficiency of the refining station and the skills of the refining player.  The refining process is taxed at a rate computed from a reference price, a station tax rate and the yield of raw materials.  We can combine the yield and tax of the refinement process with market data to determine whether an arbitrage opportunity exists, as well as the expected profit.  We can describe this process in formal terms using the following definitions:

* $r$ - an ore or ice type to be refined.
* $r_m$ - the amount of material required for one refinement cycle.
* $e$ - refinement efficiency computed from station efficiency and player skills.  This will be a value between 0 and 1.
* $m(r) \rightarrow {(c_1, v_1), ..., (c_n, v_n)}$ - a map from source material to a set of refined materials $(c_i, v_i)$ where $c_i$ represents the refined material type, and $v_i$ represents the ideal quantity produced when refining $r_m$ units of $r$.
* $p_r(t)$ - the reference price for an asset \(i.e. a price computed daily by CCP, see below\).
* $p_a(t)$ - the current best ask price for an asset \(i.e. the minimum price at which the asset can be purchased\).
* $p_b(t)$ - the current best bid price for an asset \(i.e. the maximum price at which the asset can be sold\).
* $t$ - sales tax for the refining player.  This will be a value between 0 and 1.
* $s_t$ - station refining tax which is affected by player standings towards the station.  This will be a value between 0 and 0.05.

For a given source material $r$, with refined material set $(c_1, v_1), ..., (c_n, v_n)$, the amount of refined material $c_i$ produced by refining $r_m$ units of $r$ is $v_i \times e$.  The total tax charged for the refinement process is $\sum_i\left(v_i \times e \times s_t \times p_r(c_i)\right)$.  Therefore, an arbitrage opportunity exists if the following equation is non-negative:

$\sum_i\left(v_i \times e \times \left[(1 - t) \times p_b(c_i) - s_t \times p_r(c_i)\right] \right) -  r_m \times p_a(r)$

The first term is a simplification of the equation:

$\sum_i\left(v_i \times e \times p_b(c_i)\right) - \sum_i\left(v_i \times e \times p_b(c_i) \times t \right) - \sum_i\left(v_i \times e \times s_t \times p_r(c_i)\right)$

which is, respectively, the profit from selling the refined materials, less sales tax and less refinement tax.  The last term \($r_m \times p_a(r)$\) in the opportunity equation is the cost of buying the ore or ice to refine.

The only factors in this equation which can be influenced by the player are efficiency and station refining tax.  Station refining tax is based on player standings towards the refining station and starts at 5%.  At time of writing, this tax is 0% if standing is 6.67 or better.  Efficiency is determined by the product of the following attributes:

* Station base refining efficiency \(a value between 0 and 1\).
* Reprocessing skill multiplier which is $1.0 + 0.03 \times {level}$ for a maximum of $1.15$.
* Reprocessing efficiency skill multiplier which is $1.0 + 0.02 \times {level}$ for a maximum of $1.10$.
* Ore specific processing skill multiplier \(ores only\) which is $1.0 + 0.02 \times {level}$ for a maximum of $1.10$.
* Ice processing skill multiplier \(ice only\) which is $1.0 + 0.02 \times {level}$ for a maximum of $1.10$.
* Refining implant multiplier if the refining player has an appropriate implant \(e.g. Zainou 'Beancounter' Reprocessing\).

In our research, we've found opportunities at various efficiency levels.  Thus, it is not necessary to train all skills to level 5 to benefit from ore or ice arbitrage.  However, you *will* need to train to maximum skills to maximize your profit.  It is also the case that player-owned structures can have higher base refining efficiency than NPC structures \(which typically have a base efficiency of $0.5$\).  Therefore, moving ore or ice to a player-owned structure may increase yield and hence profit.  However, this is only practical if you have a ship large enough to transfer assets efficiently.  You also incur the risk of losing your ship in transit.  A more practical approach is to look for arbitrage opportunities at player-owned structures which host both refining and market services.

With the theory established, we'll turn now to developing code to detect arbitrage opportunities.

### Example 7 - Detecting Ore and Ice Arbitrage Opportunities

In this example, we'll develop code to look for arbitrage opportunities using a day of order book market data.  You can follow along with this example by downloading the [Jupyter Notebook](code/book/Example_7_Ore_and_Ice_Arbitrage.ipynb).

The setup for this example is to choose a region, station and reference date.  Our goal is to find opportunities to buy ore or ice at our chosen station, then sell refined materials for a profit at the same station.  In this example, we'll use 'Jita IV - Moon 4 - Caldari Navy Assembly Plant' as our station in The Forge region.  Players familiar with EVE will know this is easily the busiest station in high security space.  The following cell shows our setup:

![Region and Station Setup](img/ex7_cell1.PNG)

Since we're focusing on ore and ice types, we'll need to extract type information, including refined material output for each type.  We need two pieces of information for each type we wish to refine:

1. The minimum portion size required for one refinement cycle.
2. The set of materials the type refines to, including the amount of each refined material at perfect efficiency.

For this example, we build a type map from refined asset type to type information including the items above.  We'll use this type map in our arbitrage calculations later in the example.  The next cell shows the creation of the type map:

![Type Map Creation](img/ex7_cell2.PNG)

Next, we extract order book data for our reference date.  Order book data is substantially large than market history snapshots.  Thus, we recommend that you download this data locally to make it easier to experiment with different arbitrage configurations.  We load a day of order book data into a DataFrame for further analysis:

![Download and Load Order Book](img/ex7_cell3.PNG)

As a last initialization step, we'll need to choose values for efficiency, sales tax, and station tax rate.  For this example, we've initialized these values as follows:

* $efficiency = 0.5 \times 1.15 \times 1.1 \times 1.1$ - this represents efficiency at a typical NPC station with maximum skills \(but no implants\).
* $salesTax = 0.01$ - this represents sales tax at a typical NPC station with maximum skills.
* $stationTax = 0.04$ - this is an empirical estimation which accounts for replacing market reference prices with actual prices \(see below\).

Now we're ready to look for arbitrage opportunities.  The equations we derived above are suitable for checking whether an arbitrage opportunity exists, but do not reflect how we'd typically go about looking for opportunities in data.  An actual strategy for finding arbitrage opportunities would need to simulate buying source material \(based on order book data\), then simulate refining and selling the refined materials \(also using order book data\).  We would execute this procedure on every snapshot of a historical day of data, or on the latest snapshot if we are running our strategy live.  The following pseudo-code describes a basic arbitrage opportunity finder for a day of order book data:

```
for each snapshot S:
  for each refinable asset r:
    let r_m = minimum refinable volume for r
    while profitable:
      determine whether we can buy r_m units of r
      if buy successful:
        let cost = cost of buying r_m units of r
        let gross = 0
        compute the refined materials for r_m units of r
        for each refined material m:
          determine whether we can sell m
          if sell successful:
            let gross = gross + proceeds from selling m
            let cost = cost + incremental reprocessing tax for m
          else:
            let gross = 0
            break
        if gross > cost:
          record opportunity
	else:
	  # no longer profitable
	  break
      else:
        # no more source material to buy
        break
```

This process considers all refinable assets for each snapshot.  The check for an opportunity consists of first attempting to buy enough volume of a refinable asset, then attempting to sell the refined materials.  If the gross proceeds from selling the refined materials exceeds the cost of buying the refined asset, plus reprocessing tax, then the opportunity is profitable.  We can determine whether it is possible to buy a refinable asset, or whether it is possible to sell a refined material, by consulting orders in the order book.  We maximize the profit for a given refinable asset by continuing to buy and refine until it is no longer profitable to do so.

Maximizing each opportunity is complicated because the state of orders must be maintained between each refinement cycle.  That is, orders must be "used up" as we buy and sell material over several refinement cycles.  For now, we'll implement a much simpler process which only attempts to find the *first* opportunity in a snapshot for each refinable type.  We'll derive a maximizing process later in the example.  The first function we'll implement attempts to buy enough source material at the given station to allow reprocessing to occur.  The needed volume may be filled over multiple orders.  Thus, the result of this function is a list of order pairs $(p_1, v_1), ..., (p_n, v_n)$ representing the prices and volumes of orders which were filled to buy the necessary material.  An empty list is returned if sufficient material can't be purchased:

![Buying Source Material](img/ex7_cell4.PNG)

A similar function is needed to sell refined material.  As we noted in [Example 3](#example-3---trading-rules-build-an-order-matching-algorithm), our sell algorithm must properly handle ranged buy orders.  We use the `TradingUtil` class we introduced in Example 3 to handle ranged orders properly:

![Selling Refined Material](img/ex7_cell5.PNG)

As with buying source material, our sell function will return a list of order pairs showing the prices and volumes of the orders used to complete our sell order.  If the refined material could not be sold, then an empty list is returned.

We're now ready to implement a basic opportunity checker:

![Basic Opportunity Checker](img/ex7_cell6.PNG)

The code looks complicated but it's really just an implementation of the pseudo-code above.  The main steps are:

1. Iterate through every snapshot in our order book.
2. Iterate through every refinable ore or ice.
3. Attempt to buy enough source material to refine.
4. Use the type map to determine how much refined material is produced.
5. Attempt to sell all refined material.
6. If we can sell the refined material at a profit, then record the opportunity.

The main costs are the initial purchase of the source material and the refinement tax which is charged incrementally for each refined material.  The main proceeds are the sale of refined materials less sales tax.  We're now ready to run our opportunity checker.  Note that this next cell will take several minutes to execute as we're processing an entire day of order book day \(288 snapshots\).  Incremental progress is displayed as we process snapshots:

![Checking for Opportunities](img/ex7_cell7.PNG)

We've defined a simple opportunity display function in the next cell.  Let's take a look at the results:

![Opportunity Results](img/ex7_cell8.PNG)

If you scroll down in the notebook, you'll see we detected 654 total opportunities.  For each opportunity, we report profit and *return* which is profit divided by total cost.  Return is the payout you get for risking your money on an opportunity.  All things being equal, a higher return is better.  However, arbitrage is somewhat unique in that we can tolerate low return if we can take advantage of an opportunity quickly enough \(more on this below\).

There seem to be many opportunities on our reference date, but to really value these opportunities, we need to maximize each one by buying and refining until it is no longer possible to do so.  Maximizing this way will tell us the value of each opportunity, and give us some idea of the total value of the entire day.  As we noted above, executing multiple refinement cycles for an opportunity requires that we keep order book state so we can update orders as we consume them.  The main modification, therefore, will be to our functions for buying source material and selling refined material.  We modify our "buy" function by passing in an order list instead of a snapshot.  We assume this order list represents the available sell orders for a given source material at a given location:

![Buy Function on Order Lists](img/ex7_cell9.PNG)

Our buy function has the side effect that orders in the order list we pass are updated to reflect consuming volume to fill our order.  We make a similar change to our sell function:

![Sell Function on Order Lists](img/ex7_cell10.PNG)

Our sell function has the same side effect as our buy function: orders in the order list are updated as they are consumed.  Since we'll be manipulating order lists frequently, our next cell \(not shown\) implements convenience functions for extracting buy and sell orders from a snapshot into an order list.  We're now ready to write a function which attempts to find and maximize an opportunity on a single refinable type:

![Maximizing an Opportunity on a Single Type](img/ex7_cell11.PNG)

The main change from our initial opportunity finder is the introduction of a loop which attempts to buy and refine source material as long as it is profitable to do so.  The result of this function is either `None` if no opportunity exists, or an object which describes the opportunity with the following values:

* *gross* - gross proceeds from selling refined materials \(less sales tax\).
* *cost* - total cost of purchasing source material, including reprocessing tax.
* *profit* - i.e. *gross* - *cost*.
* *margin* - *profit* / *cost*.
* *buy orders* - the list of all buy orders of source material.  Orders are aggregated by price.
* *sell orders* - a map from refined material type ID to the list of all sell orders for that type.  Orders are aggregated by price.

Finally, we can finish our opportunity finder with an outer loop that iterates through all snapshots and types:

![Finished Opportunity Finder](img/ex7_cell12.PNG)

Let's execute our new finder on our reference date.  Note that this execution will take much longer than our previous opportunity finder as each opportunity may require multiple refine iterations.  We can then display the results as before:

![Maximized Opportunity Results](img/ex7_cell13.PNG)

The same number of opportunities are found as before, but now we have information on the full extent of each opportunity.  Opportunities early in our sample day look very promising.

Based on our sample day, it looks like ore and ice arbitrage may be a viable trading strategy.  The next step is to perform a back test over a longer date range to see if arbitrage opportunities are common, or if we were just fortunate to pick this particular sample date.  Our back test should report the total value of opportunities for each day.  Note, however, that the same opportunity often persists over multiple consecutive snapshots.  Thus, simply adding all the opportunities for a day would be misleading.  Instead, we'd like to collapse multiple instances of the same opportunity into a single instance.  A simple way to do this is to collapse all consecutive opportunities for the same source material into one opportunity.  We can arbitrarily choose the first time the opportunity appears to be the representative for all consecutive appearances.  This approach isn't perfect.  It's possible that two consecutive opportunities for the same source material are, in fact, two different opportunities.  However, this simple approach will allow a reasonable approximation of the value of a day of opportunities.

The next cell \(not shown\) defines the `clean_opportunities` function which "flattens" a list of opportunities as described above.  Flattening our maximized results produces the following list and summary statistics:

![Flattened Opportunities for Sample Date](img/ex7_cell14.PNG)

From the summary results, ore and ice arbitrage seems like a promising strategy.  At 50M ISK per day, this strategy would be worth about 1.5B ISK per month with little risk \(more on that below\).  Note, also, that we've only analyzed opportunities in one region.  Other regions are likely to present opportunities as well, although one would expect these to be less frequent based on overall volume levels.  The next example constructs a back test to determine whether the long term behavior of this strategy matches the results of our sample day.

### Example 8 - Ore and Ice Arbitrage Back Test

Our initial analysis in the previous example showed that ore and ice arbitrage may be a profitable strategy.  In this example, we'll back test the strategy against a longer time range in the same region trading from the same station as in the previous example.  Our goal is to answer these key questions:

1. What are the average and median daily returns?
2. What are the average and median daily profits?
3. Are some days of the week more profitable \(or return better\) than others?
4. Are certain times of day more profitable \(or return better\) than others?
5. Are certain source materials more profitable \(or return better\) than others?

Answers to these questions will help determine the long term viability of our strategy.

We'll conduct our back test over the three month period from 2017-01-01 to 2017-03-31.  The date range is arbitrary.  We chose this date range because it is near time of writing.  Before using any strategy, it is prudent to conduct your own back test with an appropriate date range.

Unlike previous examples, we won't provide a Jupyter notebook which performs the back test.  The reason is that this back test is rather time intensive, especially if run linearly for each date in the date range \(as a simple Jupyter notebook would do\).  Moreover, this back test is [embarrassingly parallel](https://en.wikipedia.org/wiki/Embarrassingly_parallel), making it much simpler to run offline with a simple script.  To that end, we provide the [`ore_ice_arb_backtest.py`](code/book/ore_ice_arb_backtest.py) script which has the following usage:

```bash
$ python ore_ice_arb_backtest.py YYYY-MM-DD output.csv
```

This command will find all ore and ice opportunities on the given date and write those opportunities in CSV format to the specified file.  To run the complete back test, simply run this command for every date in the date range.  If you have a reasonably powerful machine, you will be able to run multiple dates in parallel.  When all dates complete, you can concatenate all the output files to make a single results file with all opportunities for our date range.

Assuming you've generated back test data \(you can also use our data which is available at [ore_ice_arb_backtest_20170101_20170131.csv.gz](https://drive.google.com/open?id=0B6lvkwGmS7a2SDBYRmJwVjhiTm8)\), we now turn to a [Jupyter notebook](code/book/Example_8_Ore_Ice_Arbitrage_Backtest.ipynb) which shows our analysis of the results.  We start by reading the opportunities file into a simple array:

![Read Collected Opportunities](img/ex8_cell1.PNG)

Next, we "clean" opportunities as in the previous example.  Cleaning joins adjacent opportunities for the same type in order to make daily profit calculations more accurate:

![Cleaning Opportunities](img/ex8_cell2.PNG)

To start, we'll group the results by day and look at a graph of profit over time:

![Daily Profit](img/ex8_cell3.PNG)

The results show a clear outlier which will make it difficult to determine whether this strategy is viable long term.  Even though the outlier might, in fact, be a valid opportunity, it is better to remove it for our analysis so that we can more accurately predict more typical behavior.  This outlier may be due to a single opportunity, or a small collection of opportunities.  To better understand the nature of the outlier, we'll graph profit for all opportunities over time:

![Profit for All Opportunities](img/ex8_cell4.PNG)

From this graph, it appears there are actually two significant outliers.  Removing opportunities above 150M ISK should be sufficient for our analysis.  Applying that adjustment, we can group by day and graph daily profit:

![Daily Profit (Less Outliers)](img/ex8_cell5.PNG)

as well as daily return \(profit / cost\):

![Daily Return](img/ex8_cell6.PNG)

From these results, it doesn't appear that our results from our test day are very common.  Profits are consistently in the small millions, and returns are likewise consistently in the low single digits.  We can confirm our intuition by computing daily average and median statistics:

![Daily Aggregates](img/ex8_cell7.PNG)

The aggregates confirm that while this strategy is profitable, we probably shouldn't focus on this approach to the exclusion of all others.  Despite the disappointing returns, let's continue our analysis to see if there is any other interesting behavior.

We know from experience that EVE tends to be more active on weekends.  Do we see the same behavior in arbitrage opportunities?  Let's look at number of opportunities and total profit grouped by day of the week:

![Opportunities (bar) and Profit (line) by Day of Week](img/ex8_cell8.PNG)

With the caution that we're only looking at three months of data in a single region, we can draw some interesting conclusions from these results:

* Tuesday has a slight edge in terms of number of opportunities, but is the clear favorite in terms of profitability.
* Despite having a large opportunity count, the weekends are not as profitable as we might expect.
* Sundays, in particular, have surprisingly low profit given the number of opportunities.

If you can only spend one day a week executing your strategy, then these results say Tuesday is the day you should choose.

What about time of day?  Grouping by hour of the day answers that question:

![Opportunities (bar) and Profit (line) by Hour of Day](img/ex8_cell9.PNG)

The count of opportunities shows a very clear progression from fewest opportunities around midnight UTC, peaking with the most opportunities at 21:00 UTC.  Profit does not quite line up with the opportunity count, however.  It's not clear whether we can infer any guidelines for our trading from this data.  Note that we could combine our day of week results with hour of day results to attempt to infer the best time of day for opportunities on known high count days \(e.g. Tuesday\).  We leave this variant as an exercise for the reader.

For our final bit of analysis, let's look at the data grouped by source material type:

![Opportunities (bar) and Profit (line) by Type](img/ex8_cell10.PNG)

We've sorted this graph by opportunity count as it seems likely that ore families will naturally group together.  In fact, we do see a distinct grouping in the plagioclase family.  This is perhaps not surprising given that plagioclase is a profitable ore in The Forge.  Conversely, an analysis in Domain might show Kernite as a more dominant ore for the same reason.  Some other pairs of ore also show grouping.  In terms of profitability, compressed dark glitter \(an ice\) is a clear outlier with a large number of opportunities as well.  This might be a focus for competitively priced bid orders to try to capture industrialists dumping excess stock on the market.

This completes our back test of our ore and ice arbitrage strategy.  Our results show that this strategy is profitable, but certainly not enough to be the main focus of any trader.  We now turn our focus to scrapmetal reprocessing as an arbitrage strategy.

## Scrapmetal Processing Arbitrage

We started our discussion on arbitrage by looking at opportunities based on ore and ice. In fact, most asset types in EVE can processed through the "scrapmetal" game mechanic which is identical to ore and ice reprocessing except for efficiency, which is affected by different skills.  As above, we can describe the scrapmetal processing mechanic in terms of the following definitions:

* $r$ - an asset type to be reprocessed (*not* ice or ore).
* $r_m$ - the amount of material required for one reprocessing cycle.
* $e$ - reprocessing efficiency computed from station efficiency and player skills.  This will be a value between 0 and 1.
* $m(r) \rightarrow {(c_1, v_1), ..., (c_n, v_n)}$ - a map from source type to a set of reprocessed types $(c_i, v_i)$ where $c_i$ represents the reprocessed type, and $v_i$ represents the ideal quantity produced when reprocessing $r_m$ units of $r$.
* $p_r(t)$ - the reference price for an asset \(i.e. a price computed daily by CCP, see below\).
* $p_a(t)$ - the current best ask price for an asset \(i.e. the minimum price at which the asset can be purchased\).
* $p_b(t)$ - the current best bid price for an asset \(i.e. the maximum price at which the asset can be sold\).
* $t$ - sales tax for the reprocessing player.  This will be a value between 0 and 1.
* $s_t$ - station reprocessing tax which is affected by player standings towards the station.  This will be a value between 0 and 0.05.

Given these definitions, an arbitrage opportunity exists if the following equation is non-negative:

$\sum_i\left(v_i \times e \times \left[(1 - t) \times p_b(c_i) - s_t \times p_r(c_i)\right] \right) -  r_m \times p_a(r)$

Note that this equation is identical to the refining opportunity equation in the previous section.  What makes scrapmetal processing different is the computation of efficiency which is determined by the following attributes:

* Station base refining efficiency \(a value between 0 and 1\).
* Scrapmetal Processing skill multiplier which is $1.0 + 0.02 \times {level}$ for a maximum of $1.10$.

There are currently no implants which affect scrapmetal processing.  As a result, maximum efficiency is much lower for scrapmetal processing as compared to ore and ice reprocessing.  However, there are many more asset types eligible for scrapmetal processing.  As we'll see below, this difference provides many more opportunities for market price imbalances which lead to arbitrage opportunities.  We'll take a look at a day of scrapmetal processing arbitrage opportunities in the next example.

### Example 9 - Detecting Scrapmetal Arbitrage Opportunities

In this example, we'll repeat the analysis we performed in [Example 7](example-7---detecting-ore-and-ice-arbitrage-opportunities), replacing ore and ice with all assets eligible for scrapmetal processing.  Because of the number of types eligible for processing, we won't generate opportunities using a Jupyter notebook.  At time of writing, there are about 8000 types we need to analyze to test for opportunities.  The most effective way to scan for opportunities is take take advantage of the embarrassingly parallel nature of the opportunity search.  Despite this optimization, analysis of a single day takes about four hours on our equipment, which is not very interesting as an illustrative example in a Jupyter notebook.  Instead, we'll use a script to generate a list of opportunities offline, then we'll load the data into a Jupyter notebook for analysis.  Our offline script, [`scrap_single_day.py`](code/book/scrap_single_day.py), has the following usage:

```bash
$ python scrap_single_day.py YYYY-MM-DD output.csv
```

As noted above, this script will take some time to execute.  Knowledgeable readers will find it beneficial to edit this script to take advantage of all available CPU cores on their particular system \(we use 10 cores on our equipment\).  We'll review the results of our single day opportunity finder for the remainder of this example.  You can follow along by downloading the [Jupyter Notebook](code/book/Example_9_Scrapmetal_Arbitrage.ipynb).

We start by loading our offline results into our notebook \(if you haven't generated your own data, you can use our data at [scrap_backtest_20170110.csv.gz](https://drive.google.com/open?id=0B6lvkwGmS7a2ci1MMmZwRDdtX28)\):

![Load and Sort Single Day Scrap Opportunities](img/ex9_cell1.PNG)

A consequence of our offline script is that results for the day are not in order, so we sort results by time after loading.  Next, we "clean" our results, as in previous examples, by collapsing adjacent instances of the same opportunity into the first instance.  We do this in the next cell \(not shown\).  Once we have cleaned results, we can take a look at opportunities for the day:

![Single Day Opportunities](img/ex9_cell2.PNG)

Our results show almost 800 distinct opportunities for the day, more than we found on the same day for ore and ice.  Many of these opportunities are small, but there are also a few large results as well.  Computing a daily summary should give us an idea of the total opportunity available:

![Single Day Summary](img/ex9_cell3.PNG)

Returns are not much better than in the ore and ice case, but profit is about three times better.  If these results are typical, then we'd expect a run rate of about 4.5B ISK per month which is very respectable given the low risk and effort required to run this strategy.  The only way to increase our certainty is to run a longer back test.  We take on that task in our next example, including a more detailed analysis of the results.

### Example 10 - Scrapmetal Arbitrage Back Test

In this example, we continue our analysis from the previous example, this time extending our analysis over a three month back test.  We'll once again consider the same questions we considered in [Example 8](example-8---ore-and-ice-arbitrage-back-test):

1. What are the average and median daily returns?
2. What are the average and median daily profits?
3. Are some days of the week more profitable \(or return better\) than others?
4. Are certain times of day more profitable \(or return better\) than others?
5. Are certain source materials more profitable \(or return better\) than others?
6. What is the distribution of opportunities?
7. Which opportunities are the most important to capture?

We'll conduct our back test over the same three month period we used for ore and ice: 2017-01-01 to 2017-03-31, inclusive.  We'll use the same offline script we used in the previous example to generate opportunity data for our date range.  The execution of the script is the same as described in the previous example, except that we execute for every day in our date range.  On our equipment, each day of data takes about four hours to generate.  Fortunately, you can run all the days in parallel if you wish.  When all runs complete, you'll have separate output files which can be concatenated into a single file of results.  Note that opportunities will be unsorted if you use our script.  We sort the data as part of our Jupyter notebook below.

Assuming you've generated back test data \(you can also use our data which is available at [scrap_backtest_20170101_20170331.csv.gz](https://drive.google.com/open?id=0B6lvkwGmS7a2dW90THBLWVRwTVU)\), we now turn to a [Jupyter notebook](code/book/Example_10_Scrapmetal_Arbitrage_Backtest.ipynb) which shows our analysis of the results.  We start by reading the opportunities file into a simple array:

![Read Collection Opportunities](img/ex10_cell1.PNG)

Next, we need to sort and "clean" opportunities as we've done in the previous example:

![Sort and Clean Opportunities](img/ex10_cell2.PNG)

We know from the previous example that there will be at least one outlier that will likely skew our results.  Skipping ahead to a graph of profit for all opportunities, we see two to three clear outliers:

![Profit for All Opportunities](img/ex10_cell3.PNG)

From inspection, removing opportunities above 250M ISK should be sufficient for our analysis.  After applying this adjustment, we can now consider daily views of profit \(all less outliers\):

![Daily Profit](img/ex10_cell4.PNG)

and return \(profit / cost\):

![Daily Return](img/ex10_cell5.PNG)

Profit is consistently strong until March, while returns remain fairly steady except for a few spikes in February.  The marked change in profit without a change in returns suggests the number of opportunities went down in March.  We can easily test this intuition by plotting opportunity count:

![Daily Opportunity Count](img/ex10_cell6.PNG)

From the graph, it is clear there is a strong drop in opportunities as we enter March.  Why would this be the case?  There are many possible explanations: seasonal effects; market activity moving elsewhere \(e.g. player-owned stations\); improved market efficiency \(unlikely\); etc.  Our back test doesn't cover a large enough time range to reveal a seasonal effect.  Likewise, we would need to perform an analysis of data from player-owned stations to determine whether there is any correlation.  We'll leave these tasks for future work.

The overall strategy seems more profitable than ore and ice.  We can confirm this intuition by considering aggregate measures:

![Daily Aggregates](img/ex10_cell7.PNG)

These numbers are, indeed, better than ore and ice, which is perhaps not surprising given how many opportunities we see.  On the other hand, maximum scrapmetal efficiency is much lower than ore and ice, so the profitability here is somewhat surprising.  The significant difference between average and median is a reflection of the slowdown in March, and the few large days early in the quarter.

Let's turn now to investigating day of week behavior:

![Opportunities (bar) and Profit (line) by Day of Week](img/ex10_cell8.PNG)

These results are quite different than ore and ice in which opportunity and profit peaked on Tuesday.  Scrapmetal arbitrage opportunities are centered around the weekend which is what we would typically expect.  However, Monday has emerged as the peak profit day for this strategy, even though most opportunities occur on Sunday.  If you can only spend one day a week executing your strategy, then these results suggest Monday is the day you should choose.

We can perform a similar analysis of time of day as well:

![Opportunities (bar) and Profit (line) by Hour of Day](img/ex10_cell9.PNG)

As is the case with ore and ice, there is a very clear runup from midnight to a peak at 20:00 (UTC).  Unlike ore and ice, however, the opportunity count peak aligns very closely with the profit peak.  Being ready to strike around 20:00 seems to be very profitable with this strategy.  The other two profitable peaks may coincide with timezone behavior.

Finally, let's look at which asset types are most profitable during the back test.  Our back test discovered opportunities for over 700 distinct asset types, far too many to view all at once.  Instead, we'll focus on the top 50 \(this threshold can easily be changed in the sample notebook\).  Here are the top 50 opportunities by count:

![Opportunities (bar) and Profit (line) Top 50 by Count](img/ex10_cell10.PNG)

Profitability roughly follows opportunity count but it may also be useful to look at top 50 by total profit.  We can create this view by sorting by total profit:

![Opportunities (bar) and Profit (line) Top 50 by Profit](img/ex10_cell11.PNG)

There is no obvious relation between opportunity count and profit shown in this graph.  However, it is useful to highlight which asset types appear in both the top 50 by count as well as the top 50 by profit:

![Opportunities (bar) and Profit (line) Top 50 by Profit - Top 50 by Count (green)](img/ex10_cell12.PNG)

About 40% of the top 50 by count are also in the top 50 by profit.  Since we're most likely to capture a frequently occurring opportunity, this indicates a good chance of also catching a profitable opportunity.

To close out our analysis of arbitrage, let's take a look at the distribution of opportunities and see if there is any useful information that might guide the construction of a trading strategy.  We'll start by constructing the histogram of opportunities by profit up to opportunities worth 10M ISK or less:

![Profit Histogram - 10M ISK or less](img/ex10_cell13.PNG)

This graph doesn't tell us much other than that the majority of opportunities are well less than 200K ISK in value.  Those opportunities might add up to significant value, but it may get tedious to have to consume so many small opportunities.  Let's zoom in on the data for opportunities up to 2M ISK in value.  We can view this data by shrinking the range of opportunity count, and lowering the profit limit:

![Profit Histogram - 2M ISK or less](img/ex10_cell14.PNG)

We see from this zoomed in view that a reasonable number of examples exist up until 1M ISK, after which opportunity counts drop significantly.  How significant is this distribution?  One way to understand significance is to determine the count and profit of opportunites outside of this range:

![Count and Profit above 1M ISK](img/ex10_cell15.PNG)

As expected, the number of opportunities above 1M ISK is very small relative to all opportunities.  However, most of the profit also resides above this line.  This suggests a simple trading strategy where we only take opportunities above 1M ISK, leaving the others for someone else.  How many opportunities might we expect at this threshold?  Is there an even better threshold below 1M ISK?  We can answer these questions by simply iterating over other threshold choices:

![Trading Statistics at Profit Thresholds up to 1M ISK](img/ex10_cell16.PNG)

The data shows a significant drop in daily opportunity count ratio, even at a threshold as low as 100K ISK.  However, the majority of daily profit ratio is still captured.  Thus, while an obvious trading strategy is to simply take every opportunity we find; these results show that this isn't necessary.  In particular, while even dedicated EVE traders may find it tedious to capture 400 \(median\) opportunities a day, they need not bother.  Instead, we can reduce the opportunity count significantly \(by choosing an appropriate threshold\), and still capture a substantial portion of daily profit.

### Analysis Limitations

The results from our analysis above carry a few caveats which are worth listing here.  Despite these limitations, our own real trading at Orbital Enterprises has been very profitable following these strategies.  Nonetheless, it is important to understand what analysis can and can't tell you:

* **Single Region** - our analysis so far has only considered The Forge region.  Although The Forge is the largest high security region by volume, a more complete analysis should include the other four main market regions \(Domain, Sinq Laison, Heimatar and Metropolis\).
* **Memoryless within Snapshots** - we treat each opportunity within a snapshot as completely independent.  In reality, opportunities often produce overlapping refined materials.  As a result, consuming one opportunity may limit the profit and return of other opportunities.  A more correct approach would be to optimize opportunities such that their order of consumption maximizes profit.  This is non-trivial to do.  We've ignored this for simplicity.
* **Memoryless across Snapshots** - just as we are memoryless within a snapshot, we treat each snapshot independently.  That is, we ignore any opportunities that may have been consumed in a previous snapshot.  It would be more correct to track order state across all snapshots as opportunities in later snapshots will be affected by consumed opportunities in earlier snapshots.  Once again, we've ignored this detail for simplicity.
* **Short History** - we've only considered three months of history in our back tests.  This is quite short by most standards although one could argue that at 288 snapshots per day, we've actually analyzed quite a bit of data.  The lack of history impacts the predictive powers of our analysis mainly in the sense that we can't forecast the nature of opportunities we're likely to see in the future.  We've provided some hand-wavy analysis around possible trading behavior \(e.g. data around most profitable days or most profitable times of day\), but a proper analysis might attempt to forecast the appearance of future opportunities \(as well as estimate the error in our predictions, which will be large given the short history\).  Instead of this analysis, we'll argue below that it's safe to simply add this strategy to your portfolio: if opportunities stop appearing, you lose nothing; when opportunities do appear, you'll incur short lived market risk as you consume, refine and sell.

Our basic analysis complete, let's turn now to a discussion of strategy effectiveness.

## Strategy Effectiveness

We've shown in the previous two sections that arbitrage can be profitable over a reasonable time range.  The main advantages of this approach are as follows:

* **Low Risk** - in it's basic form, which is essentialy parking in a station waiting for opportunities, there is very little risk to this strategy.  The primary risk is *market risk* - meaning the chance that market prices will move away from profitability between buying your source asset and selling the refined assets.  Market risk increases over time, but since most arbitrage opportunities are executed very quickly, the exposure is quite low.  You're most likely to see market risk if you wait too long between detecting an opportunity and acting on it \(assuming you don't verify the opportunity again before taking it\).  A secondary risk is *data risk* - meaning the possibility that bad market data indicates an opportunity that doesn't really exist.  Here at Orbital Enterprises we've seen this a number of times, but incidents are relatively easy to detect and avoid \(see [Beware "Ghost" and Canceled Orders](#beware-ghost-and-canceled-orders) below\).
* **Capital Insensitive** - Some might argue that this is a disadvantage, but arbitrage strategies are not influenced by the amount of capital you have to invest.  You'll need sufficient capital to cover buying and refining source material, but adding more ISK to this strategy will not increase your returns.  This is contrary to many other trading strategies in which returns are heavily influenced by the amount of capital invested.
* **Easy To Detect Competition** - Most traders worry about other traders discovering their strategies.  As more traders pile on to the same strategy, the strategy becomes less effective and returns are lower for everyone.  In general, it can be very difficult to determine whether someone else is using your strategy \(they certainly won't tell you\).  With arbitrage, however, everyone sees the same opportunities regardless of how many are trying to act on them.  At best, someone else can beat you to an opportunity.  It is, thus, very easy to determine when you have competition with this strategy.
* **Works Almost Everywhere** - Our data shows that arbitrage opportunities exist even in relatively inefficient NPC stations.  It's true that player-owned stations can refine much more efficiently, but the state of the market at time of writing still allows many profitable opportunities in NPC stations.

The main disadvantages of this approach are as follows:

* **Passive** - arbitrage, as we've described it here, is completely passive.  There will be slow days with few or no opportunities.  You can't do much but wait these out.
* **Skill Intensive** - to get the most value out of this approach, you'll need to train key skills to level five.  This is easier for ice and scrapmetal arbitrage because there are fewer skills.  For ore, however, there are ore-specific refining skills which all must be trained to level five to maximize returns[^12].
* **Compute Intensive** - capturing all available opportunities across the main market centers of EVE is a resource intensive task.  Here at Orbital Enterprises we have one machine dedicated to collecting market data \(somewhat network and compute intensive\), and a second machine dedicated to finding arbitrage opportunities \(definitely compute intensive\).  You can use more modest resources if you're only interested in one region or less frequent checks for opportunities.

In our own experience, this strategy has proven to be very profitable but not without a few mistakes along the way \(see [Practical Trading Tips](#practical-trading-tips)\).  Even with opportunities becoming less frequent in March of 2017, our average run rate is still a comfortable 100M ISK per day.  If nothing else, this is enough to pay for our monthly subscription cost \(via PLEX\).  We've thus kept arbitrage in our current portfolio of strategies.

## Variants

In this section, we consider variants to the basic arbitrage strategy we described above.

### Selling with Limit Orders

The strategies we have described so far have bought source assets and sold refined material at the market \(i.e. at the current best price, instead of using a limit order\).  However, seasoned market professionals would typically use limit orders to sell refined materials in order to maximize profit.  This practice increases risk, since market prices may move away from your fill price, but also increases profit, since your orders will capture the spread \(the difference between the best bid and best ask for an asset\).  Should we be selling refined materials with limit orders instead of simply selling into the current best bid?  Assuming spread prices are favorable, there are at least two reasons why it may be safe to sell with more profitable limit orders:

1. Refined materials from arbitrage are usually highly liquid commodity items; and
2. Highly liquid assets usually incur lower market risk because they are in demand \(i.e. they sell quickly\).

In other words, in liquid markets there should be little risk that our refined materials won't sell in a reasonable time frame.  However, there is one important caveat: we need to avoid flooding the market with atypical volumes of an asset.  As discussed in [Example 6](#example-6---a-simple-strategy-cross-region-trading), a simple rule of thumb is to avoid limit orders which sum to more than 10% of the daily volume of a refined material.

When would we expect limit orders to be more profitable then selling at the market?  To discover these opportunities, we need to adjust our opportunity equation from above to include a new term, $b$, which is the brokerage fee percentage charged for placing a limited order.  With this new term, the opportunity equation becomes:

$\sum_i\left(v_i \times e \times \left[(1 - t - b) \times p_a(c_i) - s_t \times p_r(c_i)\right] \right) -  r_m \times p_a(r)$

There are two changes from the original equation:

1. Brokerage fee, $b$, reduces sale proceeds in the $(1 - t - b)$ term; and,
2. Sale proceeds are now based on the best ask price of the refined material, $p_a(c_i)$, instead of the best bid price.

An opportunity using sell limit orders is profitable if the above equation is greater than zero.  In general, selling with limit orders instead of at the market is more profitable if the following inequality is true:

$(1 - t - b) \times p_a(c_i) > (1 - t) \times p_b(c_i)$

This equation can be reduced to the following inequality:

${{p_a(c_i) - p_b(c_i)}\over{p_b(c_i)}} > {b \over {1 - t - b}}$

The term on the left is the "return on the spread", while the term on the right is constant.  This equation can be evaluated for each refined material to determine whether to sell with limit or market orders.  In the next example, we'll investigate what affect this modified strategy has on arbitrage.  We'll arbitrarily modify our ore and ice arbitrage strategy.  The changes are identical for scrapmetal arbitrage.

### Example 11 - Ore and Ice Arbitrage with Limit Orders

In this example, we'll modify our ore and ice arbitrage strategy to sell refined material with limit orders when it is more profitable do this.  This is a minor change to the original strategy.  We'll evaluate the modified strategy on a sample day of data.  We leave it to the reader to perform a more comprehensive back test.  You can follow along with this example by downloading the [Jupyter Notebook](code/book/Example_11_Ore_and_Ice_Arbitrage_with_Limit_Orders.ipynb).

We'll use the same setup as for [Example 7](example-7---detecting-ore-and-ice-arbitrage-opportunities), where we loaded data for a target date in The Forge trading out of the station Jita IV - Moon 4 - Caldari Navy Assembly Plant.  If you've executed the notebook in Example 7, then you should already have the required market data.  If not, you may consider going back to Example 7 for a moment and executing the cell which downloads market data.  A key part of using limit orders is controlling volume so that we don't flood the market with orders which are unlikely to fill.  We propose basing these limits on a fraction of daily volume for each type.  Volume data is available from market summary data.  Thus, we use the following cell to load this data for our types of interest:

![Load Market History](img/ex11_cell1.PNG)

We're cheating a bit in the sense that a live trading strategy wouldn't have summary information available for the current day.  In that case, summary information can be sampled from prior history \(e.g. weighted average of the previous week of summary data\).  We need to introduce two new constants for limit orders as well:

1. *broker_rate* - this is the percentage fee charged for placing a limit order; and,
2. *volume_limit* - this is the fraction of daily volume which can not be exceeded by sell orders for a particular type, and for a particular opportunity.

We set these, and other constants in the next cell:

![Constants](img/ex11_cell2.PNG)

We ended Example 7 by adding code which maximized profit from each opportunity we found.  That's where we'll start for this example.  Therefore, we include the same functions for buying from or selling two orders in the order book, including related helper functions.  The first new function we need to add is a function which computes the "spread return".  As we described above, an limit order opportunity is indicated when this return value is greater than a constant based on tax rate and broker fee.  The following function computes spread return information for a given type:

![Spread Return Computation](img/ex11_cell3.PNG)

This function works by finding the best bid and ask, then computing the return as described above.  It is possible then either the best bid or best ask does not exist \(e.g. due to lack of orders in the book\).  When this happens, no spread return is computed and all orders for this material will be market orders.

We're now ready to modify our opportunity finder.  We start by modifying the `attempt_opportunity` function as follows:

* We compute a total volume limit for each refined material based on a fraction of the historic volume for this type.  The sum of all limit orders for a refined material can not exceed the volume limit.
* When selling a refined material, we use spread return to decide whether to place limit or market orders.  For limit orders, the price of the order is based on the best ask price in the order book, volume gated by the volume limit.  Market orders are unchanged.
* If an order is a limit order, then we include the broker fee when computing gross proceeds from a cell.

Our `find_opportunities` function is unmodified except that we pass new arguments for broker fee, market summary and volume limit.  With these changes in place, we're now ready to look for opportunities on our sample date.

Maximizing opportunities, along with the limit order modification, takes a significant amount of time.  It takes about an hour on our equipment to execute the next cell:

![Executing Opportunity Finder](img/ex11_cell4.PNG)

Once this cell completes, we can have a look at the results.  Note that we have modified the results display to include whether limit orders were used in an opportunity:

![Opportunity Results](img/ex11_cell5.PNG)

Every single opportunity used limit orders for some or all refined materials.  We also generated a few more opportunities than before \(43 versus 36\).  Return and profit is also higher in many cases.  Aggregates for our sample day confirm our results are better when using limit orders:

![Summary](img/ex11_cell6.PNG)

Comparable numbers from Example 7 are 47,584,077.92 ISK profit, and a return of 0.63%.  Our results from using limit orders more than doubles profit and more than triples return.  We've made the argument that these results are reasonable because we're dealing with highly liquid refined materials in volumes small enough to sell without difficulty.  However, a more careful analysis would consider market variance and try to predict how long it will take to fill all limit orders.  Despite our liquidity argument, it is still likely that one or more orders will need to be re-priced down in order to deal with the usual competition that occurs in the market.

In our own trading here at Orbital Enterprises, we've been satisfied with our results without resorting to limit orders.  Nonetheless, the strategy seems sound.  After conducting a proper back test, you may consider enabling this variant for your own trading.

### Capture "Dumping" with Buy Orders



* take advantage of "dumping" by players needing cash fast
* takes advantage of sale prices below fair market value
* minor change to math to include limit order pricing
* need to do trade analysis to find good liquid dumping targets
  * volume weighted average closer to low price is a good sign?
  * check data to verify

## Practical Trading Tips

### Keep Up with Static Data Export Changes

Arbitrage opportunities are sensitive to the ideal refined material output of source assets.  Output values are retrieved from the Static Data Export and are normally stable.  However, CCP does, periodically, rebalance the refining process, particularly for newly introduced asset types.  Missing a change can be very costly.  At Orbital Enterprises, our own trading was victimized by one such change:

![What Happens When You Miss an SDE Change](img/ch2_fig2.PNG)

In December of 2016, CCP rebalanced refining output for one of the new Citadel modules.  We missed this update to the SDE and lost about 1B ISK between December 18th and 19th due to a miscomputed opportunity.  We misdiagnosed this problem as a transient refined material order \(see next section\).  As a result, the same problem bit us again on December 24th, this time costing us about 500M ISK.  At that point, we properly diagnosed the problem.  Long story short, don't miss SDE updates!

### Beware "Ghost" and Canceled Orders

Transient orders can sometimes fool an arbitrage strategy into thinking there is an opportunity when no such opportunity exists.  We've seen this effect manifest itself in two ways:

1. Market participant mistakes in which an order is placed at the wrong price, then canceled before it can be completely filled; and,
2. "Ghost" orders \(our term, not an official EVE designation\) which appear in market data, but are actually a side effect of the way EVE's implementation fills market orders.

Canceled sell orders are easy to avoid: when you attempt to take the opportunity you simply won't find anything to buy because the order has already been canceled.  Cancelled buy orders of refined materials are harder to avoid.  We'll touch on this again below.

"Ghost" orders are market orders which appear in market data momentarily before being filled.  We believe these occur because EVE's order matching algorithm places all market orders in the order book first, then executes any fills which should occur.  Occasionally, you'll see these orders in the EVE client.  For example:

![Ghost Buy Order](img/ghost_sell_order.PNG)

The blue colored order is a buy market order we placed against the current best ask \(at the top of the image\).  In most cases, the buy order will be immediately filled and will never appear in market data \(much less the client\).  However, these orders are occasionally captured in market data.  When such an order for a refined material is captured, the arbitrage opportunity finder will see an order willing to buy a refined material at the best ask.  This price may be large enough to trigger an opportunity which, of course, will no longer be available when we attempt to take it.

As noted above, bogus sell orders for source materials are easy to avoid as they won't be available when you attempt to take the opportunity.  Bogus buy orders for refined materials are harder to detect.  However, such orders usually cause a large number of opportunities to suddenly appear.  We've seen as many as ten or more opportunities appear out of nowhere as the result of a bogus buy order.  This gives us a way to possibly detect these false positives: if a large number of opportunities suddenly appear, consider waiting one or two market data cycles before taking any opportunities.  Another strategy is to only take the first opportunity, and be prepared to sell with limit orders if the opportunity is not profitable when selling at the market.  When we've been caught by these opportunities, we've usually found that the spread in refined material prices is large enough to at least break even with limit orders.

### Use Multi-buy

As you start to capture opportunities, you'll find that many opportunities buy out several orders on the sell side which differ by a small amount.  This is often a side effect of [0.01 ISK games](https://wiki.eveuniversity.org/Trading#0.01_ISK-ing) in which market competitors strive to position their orders at the best ask price.  When this occurs, you'll see opportunities like the following \(an excerpt from a tool we've developed for our own trading\):

```
Location: Jita
Type: Mega Afocal Maser I
Profit: 1,594,440.68
Tax: 3,305,299.44
Buy Orders:
10  @ 335,999.89
72  @ 335,999.90
38  @ 335,999.97
36  @ 335,999.98
2   @ 336,000.00
3   @ 336,160.00
6   @ 336,160.13
6   @ 339,850.00
10  @ 339,900.77
101 @ 339,900.78
4   @ 339,900.89
4   @ 340,000.00
2   @ 342,998.89
6   @ 342,999.00
1   @ 342,999.98
2   @ 343,000.00
```

As you can see, the first five orders differ by a very small amount.  Buying these orders out one by one can get rather tedious.  To save our sanity, we use the "multi-buy" feature in the client.  A multi-buy order specifies a quantity to buy which is then purchased at the highest price needed to buy the requested quantity.  All orders are filled at the highest price which means you're overpaying for all but the last order, but not by much since the price difference is so small.  Here's an example from the client:

![Using Multi-Buy to Buy Out a Range of Orders](img/ch2_fig3.PNG)

In this example, we'll buy out the first four orders at price 258,899.01 ISK with fewer steps than it would take to fill the orders one at a time.  Since multi-buy always buys at the local station, you can use this same technique to buy out the entire opportunity if needed.  This may eat into profits, so use care if you decide to do this.  In the opportunity above, if we had chosen to buy out the opportunity for 303 units at 343,000 ISK we would be overpaying by 1,554,887.58 ISK which is almost as large as our expected profit.  Obviously, that would not be wise.  However, buying the first four orders with multi-buy would cost just a few ISK and would save us some time.  We leave it to the reader to devise an appropriate strategy for when to use multi-buy for their own opportunities.

[^10]: This is changing with the recently announced ["PLEX split"](https://community.eveonline.com/news/dev-blogs/plex-changes-on-the-way/) which allows PLEX to be moved into and out of a special cross region container \(called the "PLEX Vault"\) shared by all characters on a given account.  With this container, you could buy PLEX in one region with one character, move the PLEX to the vault, switch to a character in a different region \(on the same account\), then pull the PLEX from the vault and sell it.  This would allow cross-region arbitrage on PLEX prices without hauling.
[^11]: At time of writing, this page is slightly out of date.  In current game mechanics, the station owner tax is charged as an ISK amount based on refining yield, station tax and reference price, *not* as an adjustment to yield as shown on the EVE University page.
[^12]: Of course, a more careful analysis of opportunities may show it's not worth training certain ore-specific skills to level five due to lack of opportunities.  We leave this analysis as an exercise for the reader.
