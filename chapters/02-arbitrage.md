# Arbitrage

In real-world markets, arbitrage is the process of simultaneously purchasing and selling an asset \(or similar assets\) in different markets.  An arbitrage trade exploits price differences between the same asset in different markets, or between an asset and related assets in the same market.  Such differences occur because of market inefficiencies.  That is, when the price of an asset deviates from *fair market value*, which is the price at which "reasonably knowledgeable" investors are willing to trade an asset.  A "reasonably knowledgeable" investor is assumed to be implicitly aware of all the factors which influence an asset's price, which are then incorporated to select a fair price for trade.  Trading strategies we'll discuss in later chapters derive their profit from these price deviations and their eventual correction.  Price correction, however, is not required for arbitrage.  In fact, arbitrage strategies only profit while price discrepanices exist.  Can we ever be sure price discrepancies *do* exist?  Generally speaking, we don't know that this will ever be the case.  In particular, subscribers to the [Efficient-Market Hypothesis](https://en.wikipedia.org/wiki/Efficient-market_hypothesis), which states that asset prices always \(eventually\) converge to fair market value, might say that price discrepancies are either non-existent or too rare to be profitable in a modern market.  In EVE, however, we'll show that these opportunities do exist and make a respectable profit.

In EVE markets, an arbitrage trade of the same asset in different markets is not possible without hauling[^10].  Instead, arbitrage opportunites in EVE are based on assets which can be refined or reprocessed into related assets which are also sold on the market.  This type of arbitrage is similar to [Index Arbitrage](https://en.wikipedia.org/wiki/Index_arbitrage) in real-world markets.  For example, raw ores like Veldspar can be traded on the market.  But Veldspar can also be refined into Tritanium which can *also* be traded on the market.  Therefore, the fair market value of Veldspar is dependent on the price of Tritanium.  If the price of Veldspar deviates far enough below fair market value, it may become profitable to buy Veldspar, refine it to Tritanium, and sell the Tritanium.  This is the essence of the trading strategies we discuss in this chapter.

The rest of this chapter will explore arbitrage opportunities in EVE.  Impatient readers may wonder whether their time is well spent on this strategy.  Are arbitrage opportunities profitable?  If so, how much?  We won't make a habit of this, but let's take a look at performance we've been able to achieve here at Orbital Enterprises.  The following graph shows performance of our arbitrage based strategy from November 2016 through March 2017:

![Performance of an Actual Arbitrage Strategy](img/ch2_fig1.PNG)

We seeded our portfolio with 2B ISK, then executed our arbitrage strategy across the five main trading regions of EVE using only our starting balance.  We use three EVE characters to conduct our trading, placed strategically in the most active markets.  As of this writing, our balance is over 38B ISK for a profit of over 36B ISK in just under five months, or an average of about 7B ISK/month.  We haven't run the strategy long enough to uncover any seasonal effects, but it's clear late fall was more profitable than more recent returns.  We currently estimate a comfortable run rate of at least 3B ISK/month.  Compared to typical real-world market strategies, these returns are outstanding.

## What Makes Arbitrage Possible?

Before we get too far into analyzing arbitrage opportunites, it is worth briefly discussing why arbitrage is possible at all.  At its root, arbitrage is made possible by one or both of the following market behaviors:

1. when the ask price of a source material falls below fair market value price as determined by the reprocessing equation \(see below\); and/or,
2. when the bid price of one or more refined materials rises above fair market value price as determined by the reprocessing equation.

There are many reasons why prices may move.  Given our knowledge of EVE player behavior, we know that some players regularly dispose of unwanted assets at cheap prices on the market.  We also know that some players focused on mining choose to trade raw ores directly as they may lack the skills to make trading refined materials possible.  Finally, we know that there are regular spikes in refined material prices as these materials are used to build the favored assets needed for wars and general PvP.

The fact that arbitrage depends on market price moves means it is possible in some cases to actually *predict* when good opportunities will occur.  We discuss once such strategy [below](#capturing-dumping-with-buy-orders).  More generally, any price forecast algorithm has the potential to be used to predict arbitrage opportunities.

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

The only factors in this equation which can be influenced by the player are efficiency and station refining tax.  Station refining tax is based on player standings towards the refining station and starts at 5%.  This tax is 0% if standing is 6.67 or better.  Efficiency is determined by the product of the following attributes:

* Station base refining efficiency \(a value between 0 and 1\).
* Reprocessing skill multiplier which is $1.0 + 0.03 \times {level}$ for a maximum of $1.15$.
* Reprocessing efficiency skill multiplier which is $1.0 + 0.02 \times {level}$ for a maximum of $1.10$.
* Ore specific processing skill multiplier \(ores only\) which is $1.0 + 0.02 \times {level}$ for a maxium of $1.10$.
* Ice processing skill multiplier \(ice only\) which is $1.0 + 0.02 \times {level}$ for a maximum of $1.10$.
* Refining implant multiplier if the refining player has an appropriate implant \(e.g. Zainou 'Beancounter' Reprocessing\).

In our research, we've found opportunities at various efficiency levels.  Thus, it is not necessary to train all skills to level 5 to benefit from ore or ice arbitrage.  However, you *will* need to train to maximum skills to maximize your profit.  It is also the case that player-owned structures can have higher base refining efficiency than NPC structures \(which typically have a base efficiency of $0.5$\).  Therefore, moving ore or ice to a player-owned structure may increase yield and hence profit.  However, this is only practical if you have a ship large enough to transfer assets efficiently.  You also incur the risk of losing your ship in transit.  A more practical approach is to look for arbitrage opportunities at player-owned structures which host both refining and market services.

With the theory established, we'll turn now to developing code to detect arbitrage opportunities.

### Example 7 - Detecting Ore and Ice Arbitrage Opportunities

In this example, we'll develop code to look for arbitrage opportunities using a day of order book market data.  You can follow along with this example by downloading the [Jupyter Notebook](code/book/Example_7_Ore_and_Ice_Arbitrage.ipynb).

The setup for this example is to choose a region, station and reference date.  Our goal is to find opportunities to buy ore or ice at our chosen station, then sell refined materials for a profit at the same station.  In this example, we'll use 'Jita IV - Moon 4 - Caldari Navy Assembly Plant' as our station in The Forge region.  Players familiar with EVE will no this is easily the busiest station in high security space.  The following cell shows our setup:

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

Now we're ready to look for arbtrage opportunities.  The equations we derived above are suitable for checking whether an arbitrage opportunity exists, but do not reflect how we'd typically go about looking for opportunities in data.  An actual strategy for finding arbitrage opportunities would need to simulate buying source material \(based on order book data\), then simulate refining and selling the refined materials \(also using order book data\).  We would execute this procedure on every snapshot of a historical day of data, or on the latest snapshot if we are running our strategy live.  The following pseudo-code describes a basic arbitrage opportunity finder for a day of order book data:

```
for each snapshot S:
  for each refineable asset r:
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
```

This process considers all refinable assets for each snapshot.  The check for an opportunity consists of first attempting to buy enough volume of a refineable asset, then attempting to sell the refined materials.  If the gross proceeds from selling the refined materials exceeds the cost of buying the refined asset, plus reproccessing tax, then the opportunity is profitable.  We can determine whether it is possible to buy a refineable asset, or whether it is possible to sell a refined material, by consulting orders in the order book.  We maximize the profit for a given refineable asset by continuing to buy and refine until it is no longer profitable to do so.  Let's take a look at code which implements this process.

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

Our sell function has the same side effect as our buy function: orders in the order list are updated as they are consumed.  Since we'll be manipulating order lists frequently, our next cell \(not shown\) implements convenience functions for extracing buy and sell orders from a snapshot into an order list.  We're now ready to write a function which attempts to find and maximize an opportunity on a single refinable type:

![Maximizing an Opportunity on a Single Type](img/ex7_cell11.PNG)

The main change from our initial opportunity finder is the introduction of a loop which attempts to buy and refine source material as long as it is profitable to do so.  The result of this function is either `None` if no opportunity exists, or an object which describes the opportunity with the following values:

* *gross* - gross proceeds from selling refined materials \(less sales tax\).
* *cost* - total cost of purchasing source material, including reprocessing tax.
* *profit* - i.e. *gross* - *cost*.
* *margin* - *cost* / *profit*.
* *buy orders* - the list of all buy orders of source material.  Orders are aggregated by price.
* *sell orders* - a map from refined material type ID to the list of all sell orders for that type.  Orders are aggregated by price.

Finally, we can finish our opportunity finder with an outer loop that iterates through all snapshots and types:

![Finished Opportunity Finder](img/ex7_cell12.PNG)

Let's execute our new finder on our reference date.  Note that this execution will take much longer than our previous opportunity finder as each opportunity may require multiple refine iterations.  We can then display the results as before:

![Maximized Opportunity Results](img/ex7_cell13.PNG)

The same number of opportunities are found as before, but now we have information on the full extent of each opportunity.  Opportunities early in our sample day look very promising.

Based on our sample day, it looks like ore and ice arbitrage may be a viable trading strategy.  The next step is to perform a backtest over a longer date range to see if arbitrage opportunities are common, or if we were just fortunate to pick this particular sample date.  Our backtest should report the total value of opportunities for each day.  Note, however, that the same opportunity often persists over multiple consecutive snapshots.  Thus, simply adding all the opportunities for a day would be misleading.  Instead, we'd like to collapse multiple instances of the same opportunity into a single instance.  A simple way to do this is to collapse all consecutive opportunites for the same source material into one opportunity.  We can arbitrarily choose the first time the opportunity appears to be the representative for all consecutive appearances.  This approach isn't perfect.  It's possible that two consecutive opportunities for the same source material are, in fact, two different opportunities.  However, this simple approach will allow a reasonable approximation of the value of a day of opportunities.

The next cell \(not shown\) defines the `clean_opportunities` function which "flattens" a list of opportunities as described above.  Flattening our maximized results produces the following list and summary statistics:

![Flattened Opportunities for Sample Date](img/ex7_cell14.PNG)

From the summary results, ore and ice arbitrage seems like a promising strategy.  At 50M ISK per day, this strategy would be worth about 1.5B ISK per month with little risk \(more on that below\).  The next example constructs a backtest to determine whether the long term behavior of this strategy matches the results of our sample day.

### Example 8 - Ore and Ice Arbitrage Backtest

Our initial analysis in the previous example showed that ore and ice arbitrage may be a profitable strategy.  In this example, we'll backtest the strategy against a longer time range.  Our goal is to answer these key questions:

1. What are the average and median daily returns?
2. What are the average and median daily profits?
3. Are some days of the week more profitable \(or return better\) than others?
4. Are certain times of day more profitable \(or return better\) than others?
5. Are certain source materials more profitable \(or return better\) than others?

Answers to these questions will help determine the long term viability of our strategy.

We'll conduct our backtest over the three month period from 2017-01-01 to 2017-03-31.  The date range is arbitrary.  We chose this date range because it is near time of writing.  Before using any strategy, it is prudent to conduct your own backtest with an appropriate date range.

Unlike previous examples, we won't provide a Jupyter notebook which performs the backtest.  The reason is that this backtest is rather time intensive, especially if run linearly for each date in the date range \(as a simple Jupyter notebook would do\).  Moreover, this backtest is [embarrassingly parallel](https://en.wikipedia.org/wiki/Embarrassingly_parallel), making it much simpler to run offline with a simple script.  To that end, we provide the [`ore_ice_arb_backtest.py`](code/book/ore_ice_arb_backtest.py) script which has the following usage:

```bash
$ python ore_ice_arb_backtest.py YYYY-MM-DD output.csv
```

This command will find all ore and ice opportunities on the given date and write those opportunites in CSV format to the specified file.  To run the complete backtest, simply run this command for every date in the date range.  If you have a reasonably powerful machine, you will be able to run multiple dates in parallel.  When all dates complete, you can concatenate all the output files to make a single results file with all opportunities for our date range.

Assuming you've generated concatenated backtest results, we now turn to a [Jupyter notebook](code/book/Example_8_Ore_Ice_Arbitrage_Backtest.ipynb) which shows our analysis of the results.  We start by reading the opportunities file into a simple array:

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

With the caution that we're only looking at three months of data, we can draw some interesting conclusions from these results:

* Tuesday has a slight edge in terms of number of opportunities, but is the clear favorite in terms of profitability.
* Despite having a large opportunity count, the weekends are not as profitable as we might expect.
* Sundays, in particular, have surprisingly low profit given the number of opportunities.

If you can only spend one day a week executing your strategy, then these results say Tuesday is the day you should choose.

What about time of day?  Grouping by hour of the day answers that question:

![Opportunities (bar) and Profit (line)  by Hour of Day](img/ex8_cell9.PNG)

The count of opportunities shows a very clear progression from fewest opportunites around midnight UTC, peaking with the most opportunities at 21:00 UTC.  Profit does not quite line up with the opportunity count, however.  It's not clear whether we can infer any guidelines for our trading from this data.  Note that we could combine our day of week results with hour of day results to attempt to infer the best time of day for opportunities on known high count days \(e.g. Tuesday\).  We leave this variant as an exercise for the reader.

For our final bit of analysis, let's look at the data grouped by source material type:

![Opportunites (bar) and Profit (line) by Type](img/ex8_cell10.PNG)

We've sorted this graph by opportunity count as it seems likely that ore families will naturally group together.  In fact, we do see a distinct grouping in the plagioclase family.  This is perhaps not surprising given that plagioclase is a profitable ore in The Forge.  Conversely, an analysis in Domain might show Kernite as a more dominant ore for the same reason.  Some other pairs of ore also show grouping.  In terms of profitability, compressed dark glitter \(an ice\) is a clear outlier with a large number of opportunities as well.  This might be a focus for competitively priced bid orders to try to capture industrialists dumping excess stock on the market.

Thus completes our backtest of our ore and ice arbitrage strategy.  Our results show that this strategy is profitable, but certainly not enough to be the main focus of any trader.  In our [Sample Trading Strategy](#a-sample-trading-strategy) section below, we recommend periodically checking for these opportunities in an automated fashion.

Now we turn our focus to scrapmetal reprocessing as an arbitrage strategy.

## Scrapmetal Reproccessing Arbitrage

* Introduce reprocessable items
* Many more opportunities since many more reprocessable types than ores
* Derive reprocessing formulas
  * Describe the skills that matter
* Derive check to determine whether asset can be reprocessed for profit
  * Must include trade model (sales tax)
  * Demonstrate on a day of book data
* Show results of three month backtest

## Strategy Effectiveness

* Advantages
  * Low risk in basic form, not necessary to leave station
  * Market risk also low in basic form
  * Not really influenced by investment amount.  You'll need sufficient capital to cover opportunities, but adding more ISK doesn't increase your returns (true of most arbitrage).
  * Easy to figure out if there is competition.  You'll see opportunities, but someone else will take them first
  * Even works in relatively inefficient NPC stations (player-owned stations can refine more efficiently)
* Disadvantages
  * Passive, there will be slow days
  * Capturing all opportunities requires significant compute resources

## Variants

### Selling with Limit Orders

* changes math on profit
* incurs more market risk (covered in later chapter), but on high volume assets so lower risk
* need to be aware of volumes on sold assets and effect of market participation (e.g. market impact)
  * define market impact

### Capture "Dumping" with Buy Orders

* take advantage of "dumping" by players needing cash fast
* takes advantage of sale prices below fair market value
* minor change to math to include limit order pricing
* need to do trade analysis to find good liquid dumping targets
  * volume weighted average closer to low price is a good sign?
  * check data to verify

### Cross-Region Reprocessing Arbitrage

* buy in one market, then transport and reprocess in another market
* incurs both market and transport risk (covered in later chapter)

## Practical Trading Tips

### A Sample Trading Strategy

### Beware "Ghost" Orders

* Market implementation posts orders before execution
  * dumping shows up as someone willing to sell reproc targets at low price
  * buys show up as someone willing to buy reproc output at a high price
* Occasionally these are captured in order book snapshots
* Causes numerous bogus arb opportunities
* Usually easy to detect as a large number of opportunities suddenly appearing

### Use Multi-buy

* Many opportunities buy out several orders
* 0.01 ISK effects cause order bunching
* Can be bought out efficienctly with multi-buy with small effect on profit

## For Further Analysis

* Analyze the expected lifetime of a strategy
* After accumulating history, look for common buyers and sellers and their behavior
* Analyze which types produce the most opportunities.  May be highly region dependent.

[^10]: This is changing with the recently announced ["PLEX split"](https://community.eveonline.com/news/dev-blogs/plex-changes-on-the-way/) which allows PLEX to be moved into and out of a special cross region container \(called the "PLEX Vault"\) shared by all characters on a given account.  With this container, you could buy PLEX in one region with one character, move the PLEX to the vault, switch to a character in a different region \(on the same account\), then pull the PLEX from the vault and sell it.  This would allow cross-region arbitrage on PLEX prices without hauling.
[^11]: At time of writing, this page is slightly out of date.  In current game mechanics, the station owner tax is charged as an ISK amount based on refining yield, station tax and reference price, *not* as an adjustment to yield as shown on the EVE University page.
