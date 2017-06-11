# Market Making \(Station Trading\)

In real-world markets, a market maker is a market participant that maintains an inventory of assets \(e.g. stock\) so that they are able to buy or sell assets to other market participants as required.  Market makers help keep real-world markets running efficiently by providing *liquidity*, which is the ability to readily trade assets at stable prices.  Real-world market makers are compensated for the risk they take in maintaining an inventory of assets.  In some markets, this compensation takes the form of rebates offered to market participants willing to provide liquidity.  In most markets, however, market makers profit by maintaining a *spread* which is the difference in price between the current best bid and best ask.  A market maker can buy assets at the best bid \(assuming a willing counterparty\), then turn around and sell those assets at the best ask, pocketing the *spread* \(or vice versa for selling at the ask and buying at the bid\).  As long as the spread is greater than associated trading fees, the market maker will make a profit.  Note, however, that profit margins are typically very thin.  In real world markets, market making is a volume game.

EVE markets do not have sponsored market makers like real-world markets.  However, many players perform a similar function and profit in a similar fashion.  These players are referred to as "station traders" because they typically never leave the station they are trading in: all assets are bought and sold in the same station.  For all intents and purposes, however, station traders are really market makers: they compete with other players to have the best bid or ask, and they profit when they can buy assets at the best bid and re-sell those assets at the best ask \(or vice-versa\).  Besides hauling, market making is one of the most popular occupations for players pursuing a market trader play style.  Part of market making's popularity stems from the fact that little capital is required to get started.  To wit, there are numerous online videos explaining how to make quick ISK by market making.

In this chapter, we'll analyze market making as a trading strategy in EVE.  We'll discuss the basics of profitability, and then work through the discovery of which assets provide good market making opportunities.  As market making is a time consuming activity, we'll also attempt to estimate how frequently you'll need to monitor your orders.  Less active players may want to use the results from this section to choose market making opportunities which fit better with their play style.  We'll also talk briefly about market risk as this is the most significant risk factor for market making.  As in earlier chapters, we provide several examples illustrating how we derive opportunities and predict outcomes.  We conclude this chapter with a brief discussion of variants and practical trading tips.

## Market Making Basics

A simple EVE market making strategy first buys assets at the best bid, then sells these assets at the best ask.  All trading occurs within a single station.  Limit orders are placed for both the bid and ask \(incurring broker fees\), and sales tax is charged when ask orders are filled.

Given the following definitions:

* $p_a$ - the best ask price for an asset
* $p_b$ - the best bid price for an asset
* $n$ - the number of assets bought and sold
* $t$ - station sales tax
* $b$ - station broker fee

the total profit, $r$, obtained by making a market for a given asset type is:

$r = p_a \times n - p_a \times t \times n - p_a \times b \times n - p_b \times b \times n - p_b \times n$

where the first term is the gross profit, and the remaining terms reflect sales tax, broker fees for placing limit orders, and the cost of buying assets at the best bid.  A market making transaction is profitable when $r > 0$. That is, when:

$p_a \times n - p_a \times t \times n - p_a \times b \times n - p_b \times b \times n - p_b \times n > 0$

or, by re-arranging terms:

${p_a \over p_b} > {{1 + b}\over{1 - t - b}}$

This last expression gives us a simple test to determine whether an asset is currently profitable for market making \(the terms on the right are all constant\).  It also tells us that if we buy the asset at the bid price, $p_b$, then we must in turn sell the asset for at least ${{1 + b}\over{1 - t - b}} \times p_b$ in order to make a profit.

If an asset is profitable for market making, then we'd also like to determine the expected return for this strategy.  From the last chapter, we know that return is ${{gross}\over{cost}} - 1$.  Given the same definitions above, the expected return is therefore:

${{p_a}\over{p_a \times t + b \times (p_a + p_b) + p_b}} - 1$

Beyond profitability, this last expression allows us to filter for market making opportunities which exceed a certain return.  Note that neither the profitability formula, nor the return formula contain a term describing the number of assets bought or sold.  In reality, the volume transacted is an important factor as markets have a fixed capacity which can change over time.  We'll consider the volume question again later in the chapter.

Market making as a trading strategy in EVE has two important limitations which must be taken into consideration:

* The price of an order can be changed without canceling the order \(which may incur a fee, see below\).
* Orders may be changed \(including cancels\) at most once every 5 minutes.

It is common for market makers to periodically change order prices to capture the best bid or ask.  At time of writing, each such change costs 100 ISK plus an additional broker fee if the original fee charged for the order does not cover the fee that would be charged for a new order at the new price.  For example, suppose a player places a buy order at 10 ISK which incurs a broker fee of 0.25 ISK per unit of asset.  If the player later changes the price of this order to 20 ISK, then the player will pay an additional 0.25 ISK in brokers fees for each asset.  This is to prevent players from "low balling" orders by placing them at a price optimized for low fees, then later changing the price.

The limit on order change frequency has the practical consequence that in competitive markets, bad timing may lead to one of your competitors changing their order just after you've changed yours.  Your order is then stuck outside the best bid or ask until the change timer expires.  An obvious strategy for avoiding this issue is to spread your position across multiple orders.  We discuss this topic towards the end of this chapter.

We've claimed that market making is a very popular strategy in EVE.  Can we detect which assets are subject to market making?  Can we tell how many participants are making a market in a given asset?  We explore the answer to these questions in our first example for this chapter.

### Example 13 - Detecting Market Making

In this example, we'll consider two questions:

1. How many assets are subject to market making? and,
2. How many players are trying to make a market in a given asset?

Orders in EVE's markets are anonymized, so answers to these questions will be estimates at best.  However, we *can* exploit known behavior to refine our answers.  Specifically:

* Market makers place their buy and sell orders at a single station with range "station";
* Assets subject to active market making will have frequently changing best bids and asks as market participants compete to capture order flow;
* Market makers frequently change price and this operation preserves order ID.  Therefore, we can detect active market makers by looking for frequently changed orders; and,
* EVE always shows distinct orders, even if orders have the same price.  This means we can at least put an upper bound on the number of market participants \(a single participant can have multiple orders for an asset, so this can't be an exact bound\).

We'll attempt to determine how many assets are subject to market making by counting the number of times the best bid or ask change at a target station.  From this count, we can estimate which assets are likley subject to active market making.  To detect how many players are actively trying to make a market, we'll look for orders which change frequently and assume each changing order indicates at least one market participant.  If the same order changes over many order book snapshots, then we can infer how frequently a particular market participant is active in the market.  All of this analysis will only make sense for reasonably liquid assets.  Therefore, we'll filter for assets with a certain number of daily trades before filtering for active market making.  As with our other examples, you can follow along by downloading the [Jupyter Notebook](code/book/Example_13_Detecting_Market_Making.ipynb).

Our first task will be to filter for liquid assets since such assets are most likely to be good targets for market making.  We use the same liquidity filter framework from previous examples, but with a much simpler liquidity filter predicate function:

![Market Making Liquidity Filter](img/ex13_cell1.PNG)

For market making, we'll test for assets which trade for a minimum number of days, and have a minimum number of orders each day.  For this example, we'll filter across 30 days of market history leading up to our target date.  We'll require at least 500 orders for each trading day as well.  Given these constraints, we can then filter for liquid assets:

![Liquid Asset Filter Results](img/ex13_cell2.PNG)

Our results show about 100 assets which meet our criteria.  You can change these criteria as needed for your own trading.  Note, however, that admitting more assets will increase analysis time and likely require more memory.

Now that we have our target assets, we're ready to load order book data for our target date \(note, also, that we're filling order book gaps as described in [Example 4](#example-4---unpublished-data-build-a-trade-heuristic)\).  Since we're analyzing market making specifically, we can filter the book down to just those orders placed at our target station:

![Order Book for Market Making](img/ex13_cell3.PNG)

Our first task is to determine which assets have the most active bid and ask orders.  Frequent changes to the best bid or ask show competition in the market.  We can compute change frequency simply by checking for changes to the best bid or ask between order book snapshots.  We'll define three simple functions to compute best bids, best asks, and to check whether orders are identical.  For the purposes of market activity, the best bid or ask has changed if a new order has replaced the previous order, or if the price has changed:

![Best Bid, Best Ask and Order Equivalence Check](img/ex13_cell4.PNG)

We can then compute change frequency for each type by tabulating best bid/ask changes between snapshots.  The following function performs this calculation and returns a Pandas DataFrame with the change time for every asset:

![Function to Compute Best Bid/Ask Changes](img/ex13_cell5.PNG)

The next two cells invoke this function on the order book over our liquid assets.  We can view the most active assets by counting the number of times each asset changes.  Let's take a look at the top 10 results:

![Top 10 Most Active Assets](img/ex13_cell6.PNG)

You may recall there are 288 order book snapshots in a day.  None of our liquid assets has a change count equal to this value, so we know none of these assets change every snapshot.  However, there are 23 assets which changed at least 144 times, or once every other snapshot \(on average\).  There are almost certainly active market makers trading on these assets.

An asset which changes more than 48 times is, on average, changing every 30 minutes.  All but 13 of our asset list meet this criteria.  However, as we lower the change frequency, it becomes more likely that changes may be grouped together over a smaller time period.  There are at least two ways we can improve our intuition around the spacing of changes for an asset:

1. We can plot the times when changes occurred; and,
2. We can look for clusters in the data showing times when there were frequent changes.

As an example, let's look at "Conductive Polymer" which changed 63 times on our target day.  The following plot shows the time of each change during the trading day:

![Best Bid/Ask Changes for Conductive Polymer](img/ex13_cell7.PNG)

The plot shows an obvious gap of about two hours at mid day.  Also, there appear to be clusters of trades and certain times of day.  One way to better understand clustering effects is to resample the data and count the number of bid/ask changes in each re-sampled interval.  This is also a way to determine the most active times of day for a given asset.  The next cell computes cluster size for three different re-sampling frequencies:

![Change Clusters for Conductive Polymer at 60, 30 and 15 minutes](img/ex13_cell8.PNG)

The mid day gap is very obvious in the 15 minute re-sampled data.  Conversely, the 60 minute sampled data shows the most active times of day (at about 05:00, 17:00 and 20:00).  As you might expect, active times are most relevant for less active instruments.  Very active assets show no real gaps.  To see this, we can look at the plot of changes for "Prototype Cloaking Device I", the most active asset on our list:

![Best Bid/Ask Changes for Prototype Cloaking Device I](img/ex13_cell9.PNG)

Astute readers may have noticed that both Conductive Polymers and Prototype Cloaking Devices show a very similar gap around 12:00 UTC.  This time range corresponds to daily downtime for EVE when no trading can occur.  Although down time is typically less than 30 minutes, trading on most assets consistently lags around this time.

From this example, it seems that counting best bid/ask changes is a simple way to identify likely market making candidates.  Let us turn now to estimating how many players are actively making a market for a given asset.

One way to identify an active market maker is to look for an order which changes frequently throughout the day.  Such orders will have the same order ID, but will change price one or more times as the owning player attempts to capture the best bid or ask.  If we simply counted the number of orders which change throughout the day, we'd likely have an overestimation of the number of active market participants because different players may participate at different times of the day.  Instead, we'll re-sample the order book over a configurable interval and tabulate the number of orders which change in a given interval.  This is still an estimate because some market participants may change their orders less frequently than our re-sampling interval.  However, results should be reasonable given a sufficiently large re-sampling interval.

A function to compute the number of orders changing for each type in a sampling interval is just a slight variant of our function for counting best bid/ask changes:

![Function to Count Changing Orders per Interval](img/ex13_cell10.PNG)

The result of this function is a Pandas DataFrame which gives the number of orders which changed at least once in a given resampling interval.  Let's look again at Conductive Polymers to see what this data looks like for an infrequently traded asset.  To provide more context, we'll overlay a plot of the change count data we computed above, resampled to the same interval we used for market participants.  Here's the plot for Conductive Polymers:

![Conductive Polymers Participants (bar - left axis) vs. Best Bid/Ask Changes (line - right axis) (1 hour samples)](img/ex13_cell11.PNG)

The peaks in the graphs do not quite line up and the sampled participant count is quite low.  One conclusion we might draw from this data is that market making is not really happening for Conductive Polymer.  Another possible conclusion is that the change cycle is much slower than one hour.  We can check out intuition by resampling for a larger change interval.  Here's the same plot for Conductive Polymer re-sampled over two hour intervals:

![Conductive Polymers Participants (bar - left axis) vs. Best Bid/Ask Changes (line - right axis) (2 hour samples)](img/ex13_cell12.PNG)

Changing the sample interval has not captured more market participants which reinforces the hypothesis that market making is probably not occuring on this asset.  Instead, this could be one large order competing with a regular flow of small orders placed by casual players throughout the day.  The owner of the large order must regularly re-position to capture the best bid or ask.  We can confirm our hypothesis by looking more carefully at the order book snapshots for the day.  We leave that task as an exercise for the reader.

What do participants look like for a more actively traded asset?  Let's look at the same plot for Prototype Cloaking Device I, sampled at one hour intervals:

![Prototype Cloaking Device I Participants (bar - left axis) vs. Best Bid/Ask Changes (line - right axis) (1 hour samples)](img/ex13_cell13.PNG)

From this plot, we see that there may be as many as 14 active market participants in a given hour of trading for this asset.  That's a lot of competition!  If we decide to trade this asset, we likely won't be successful if we plan on updating our prices once an hour.  What if we update our orders every 30 minutes?  We'll finish this example by looking at the sample plot sampled at 30 minute intervals:

![Prototype Cloaking Device I Participants (bar - left axis) vs. Best Bid/Ask Changes (line - right axis) (30 minute samples)](img/ex13_cell14.PNG)

The number of participants per interval has gone down by 30-50% in most cases, but is still quite large in some intervals.  It seems unlikely that you'll get away with updating your orders once every 30 minutes in this asset type.  If you want to trade this asset successfully, you'll likely need to be watching it all day \(more on this later\).

In this example, we've introduced a simple filter for finding asset types for which markets are likely being made.  We've also created a simple technique to estimate the number of participants making a market in a given type.  Note, however, that we've restricted our analysis to a single day, so the usual caveats apply.  A more proper analysis would consider active assets over a larger time range.  We'll discuss back testing later in this chapter.

## Selecting Markets

The example in the previous section considered the question of how many assets are subject to market marking, and how competitive are the markets for those assets.  In this section, we'll expand on this theme and derive tests to find good candidates for a market making strategy.  Some of our criteria will depend on personal play style.  Therefore, the approach we describe below may need to be customized depending on how many hours a day you'd like to spend managing your strategy.  We'll show the impact of these choices when we consider testing our strategy later in the chapter.

We'll select promising assets for market making by considering five criteria:

1. **Liquidity** - prices must be reasonably well behaved, and there must be a steady supply of willing market participants in order for a market making strategy to be successful.
2. **Profitable Spreads** - spreads for our chosen asset must be profitable \(according to the formula we derived earlier in the chapter\) on a regular basis \(i.e. over a reasonable historical back test\).
3. **Return** - we'll only want to spend our time on assets which offer a reasonable return on investment.
4. **Balanced Volume** - since market making buys **and** sells, we'll need a steady supply of willing market participants on both sides of the order book.
5. **Competition** - the amount of competition we can tolerate will be determined by how frequently we're able to be online updating our orders.

These criteria are straightforward to evaluate using the tools we've already developed in the first chapter, and earlier in this chapter.  We demonstrate this process in the next example.  Unlike previous examples, we'll focus our analysis on a single day of the week \(or rather, a history made up of the same day of the week for several months\).  We do this because market making strategies are volume sensitive, but EVE market volume changes substantially during the week.  It's possible to develop a strategy which adjusts during the week, but that is an advanced topic beyond the scope of this chapter.  For our remaining examples, we'll only consider trading on Saturdays \(typically the highest volume day of the week\).

### Example 14 - Selecting Market Making Targets

We'll work through the asset criteria we listed above in order.  Unless otherwise specified, we assume we've already downloaded all the necessary market data for this example.  If you insist on running the example with data retrieved online, simply remove the `local_storage` option in the appropriate places.  As with our other examples, you can follow along by downloading the [Jupyter Notebook](code/book/Example_14_Selecting_Market_Making_Targets.ipynb).

As with our other examples, we'll evaluate market making candidates at the busiest station in The Forge.  For historic data, we'll use every Saturday starting from 2017-01-07 through 2017-05-20.  This gives us 20 days worth of sample data.  Our liquidity filter is similar to that used in the previous example: we require an asset to have market data for every day in our sample period; we require price weighted volume to exceed a minimum threshold; and, we require a minimum number of trades \(i.e. order count\) in each day.  These criteria suggest matching assets will trade consistently over our date range with a price weighted volume large enough to yield reasonable profit.  The following figure shows our specific liquidity filter:

![Market Making Asset Liquidity Filter](img/ex14_cell1.PNG)

In this example, we'll require assets to have at least 250 trades a day.  This is a somewhat arbitrary choice.  You can increase or decrease this threshold to further exclude or include assets, respectively.  Executing our liquidity filter reduces the set of assets under consideration to 138:

![Filtering For Liquidity](img/ex14_cell2.PNG)

Our next two filters consider profitability and return using the equations defined earlier in this chapter.  We can actually combine these filters into a single filter since any asset with a positive return must also be profitable.  Therefore, we'll only compute return and use our filter to retain those assets which meet a particular return threshold.  From above, we know that return is determined by the equation:

${{p_a}\over{p_a \times t + b \times (p_a + p_b) + p_b}} - 1$

where:

* $p_a$ - the best ask price for an asset
* $p_b$ - the best bid price for an asset
* $t$ - station sales tax
* $b$ - station broker fee

The order book will provide best bid and ask prices, but we'll need to pick specific values for sales tax and broker fee.  For this example, we'll use 1% and 2.5%, respectively, which are typical values at an NPC station with maximum skills.  For each asset, we'll compute return for each snapshot in each order book over our date range.  It is rarely the case that returns are consistent from snapshot to snapshot, much less from day to day.  Therefore, we'll use the median of the snapshot returns to represent the return for an asset for a given day.  We'll include an asset if median return exceeds our target return for at least half the days in our date range.  We'll set our target return at 5%.  Once again, these are arbitrary choices.  You can tighten the filter by using a lower quantile for representing daily return; by increasing the number of days for which the return target must be met; or, by increasing the return target.  The following code produces a Pandas DataFrame of daily returns for each asset in our date range \(NOTE: this cell may take several minutes to execute due to the amount of data processed\):

![Computing Median Returns](img/ex14_cell3.PNG)

Once we have daily return data, we can apply the filter.  In this example, the filter reduces the set of assets under consideration to 28:

![Application of Return Filter](img/ex14_cell4.PNG)

Our next filter requires that we infer trades as we need to count the number of trades on each side of the book.  We'll use the same trade inference function we've used for the last few examples.  The main feature of this inference function is that complete fills and cancels are distinguished according to a fraction of average daily volume.  The next cell loads an extended range of historic market data and computes the moving average volume thresholds we need for trade inference.

Our side volume collector is a simplified version of trade inference in which we only need to count volume, not produce a list of trades.  The following code performs this function:

![Side Volume Collector](img/ex14_cell5.PNG)

We now apply this collector to our data range in order to produce a Pandas DataFrame containing buy and sell trade volume for each asset on each day:

![Computing Side Volume](img/ex14_cell6.PNG)

How are buy and sell volume related for promising market making assets?  In an ideal world, buy and sell volume would each consume half of the daily volume.  This would indicate roughly equal opportunities to buy and sell in the market, which is exactly what is needed for effective market making.  In reality, volumes are never this well matched.  For this example, we'll consider an asset a good market making target if both buy and sell side volume consume at least 20% of the daily volume.  We'll keep the assets which have this property for each day in our date range.  Once again, this is an arbitrary choice.  You can tighten the filter by requiring a larger percentage of daily volume.  Note that the volume balance between sides also gives us a hint as to how much market making volume we could expect to transact on a given day.  In particular, market making volume can't exceed the minimum of buy and sell side volume.

With some minor manipulation, we can use the side volume data to determine which assets regularly exceed 20% of volume on both sides of the book.  Applying this filter reduces the set of assets under consideration to 11:

![Application of Side Volume Filter](img/ex14_cell7.PNG)

Our final filter considers how much competition we're likely to face when making a market for a given asset.  We explored this topic in the previous example where we estimated competition by counting the number of times an existing order changed in a given time period.  Orders which change frequently show competition as market makers strive to capture the best bid or ask.  The choice of sampling period should be a multiple of how frequently you plan to update orders.  For example, if you plan to update orders every ten minutes, you should choose a sampling period of at least ten minutes, with larger multiples preferred.  Assuming competition is evenly distributed, the sample interval divided by the number of changes indicates how frequently your orders may be displaced.  In order to consistently capture the top of the book, you'll need to maintain enough orders to allow an more frequent updates than the competition.  For this example, we'll choose a sample interval of 30 minutes.  We're now ready to count orders changes using the same code from the previous example \(we've pasted that code into the next cell\).  The result will be a Pandas DataFrame giving the number of orders which changed in each sampling interval for each type on each day:

![Counting Order Changes](img/ex14_cell8.PNG)

How much competition is acceptable?  Once again, the choice is highly subjective.  However, before we consider this question, we can simplify the analysis by scoping the data to the times we know we'll be active.  In this example, let's assume we'll be actively trading from 1200 to 2400 UTC.  We can therefore eliminate order change count data outside of this region.  With the remaining data, let's look at four possible statistics we could use to decide acceptable competition levels:

1. *Average Change Count* - we could compute the average order change count per interval.
2. *Median Change Count* - we could compute the median order change count per interval.
3. *Maximum Change Count* - we could compute the maximum order change count across all intervals.
4. *Quantile Change Count* - we could compute some other quantile \(besides median\) change count per interval.

The choice here is important because our estimate of order change count is a rough measure of the number of orders we'll need to maintain in order to consistently capture the top of the book.  That is, because we can't be sure when our competitors have finished changing their orders, we need to be sure we always have at least one order we can change to capture the top of the book just after a competitor has done the same.  Average or median change count will give us some expectation of what a typical sample period might look like in terms of competition, but we risk undershooting the number of orders we need to maintain if the average or median are unusually low.  Conversely, a measure of maximum count shows how extreme the competition might get.  Using maximum is the conservative choice, but also increases the number of orders we need to maintain.   Finally, we could use a quantile other than median, say the 95% order change count quantile.  This would tell us, for example, the maximum change count for 95% of the sample intervals.  Using a high quantile measure captures the more "typical" worst case competition, as opposed to maximum which may represent an extreme outlier.  Before we decide, let's look at all of these measures for our current list of market making targets:

![Market Making Competition Measures](img/ex14_cell9.PNG)

Average and median measures suggest orders will need to be updated at most once every ten minutes, whereas maximum shows more extreme competition with some orders changing almost every minute.  If we went with the average or median measures, we'd likely conclude that none of these assets are particularly competitive \(and therefore we should trade them all\).  However, the high maximum value may give us pause: it's not clear whether the maximum is an extreme outlier or whether there are occasional runs of extreme competition.  This is where a high quantile measure can help \(we could also simply graph the data and attempt to look for extremes visually\).  The 95% quantile shows the maximum order change count for 95% of the sample intervals.  In this example, the 95% measures are roughly 60% of the maximum suggesting the maximums are infrequent outliers.  For the sake of completing this example, we'll choose to filter assets in which the 95% order change count is ten or greater.  For the assets which remain, we may need to update orders at most once every three minutes.  We can achieve this goal by maintaining two orders per asset \(since orders can be changed at most once every five minutes in EVE's markets\).

There are many other forms of analysis we could have considered for order change count.  For example, we could have analyzed change counts separately for bid and ask orders.  Likewise, we could have factored in time of day more explicitly to try to analyze where competition is heaviest.  We leave these variants as an exercise for the reader.

We've filtered the set of all assets down to a hopefully promising list of market making targets.  While we could simply trade these assets and hope for the best, a better approach is to attempt to simulate trading outcomes.  We consider this topic next.

## Testing a Market Making Strategy

Once we've chosen a set of target assets and formulated our market making strategy, how do we go about validating whether our strategy will be successful?  Ultimately, we can't know for sure until we perform real trading, but a back test against historical data may give us some confidence that we're on the right track, or at least allow us to eliminate very poor strategies.  A back test for market making \(or any trading for that matter\) is more complicated than arbitrage because with arbitrage we were guaranteed we could complete a buy and sell as long as we acted quickly enough.  We can't make the same guarantees with market making.  Instead, we need to simulate our strategy in an environment which approximates real trading.  This environment will maintain a simulated order book, and will emulate the arrival of new orders and trades.  If our environment doesn't make too many simplifications, and if our strategy is profitable in our environment, then we can have some confidence that our strategy will be successful in real trading.

In this section, we'll develop a simple trading simulator mostly suitable for testing market making strategies \(we'll consider simulation of other types of trading in a later chapter\).  Given a test strategy, a basic market simulation has three components:

1. a *market data system* which provides a view of market data to our strategy;
2. an *order management system* which allows our strategy to submit, update or cancel orders; and,
3. a *fill simulator* which simulates market activity, including filling our strategy's orders.

Note that by replacing certain components of this system, you can turn the simulator into a trading platform.  For example, you can add a *market data system* which provides live updates from EVE's markets; you can replace the *order management system* with the EVE client \(with manual order entry, of course\); and you can replace the *fill simulator* with actual market results.

We've implemented a straightforward event-based simulator consisting of the three components described above.  We won't describe the details of the implementation here.  Instead, we'll focus on the fill simulator or, more specifically, the underlying trading models which allow the fill simulator to emulate market activity.   We'll demonstrate a complete simulation, including the preparation of the fill simulator, later in the chapter.

The purpose of the fill simulator is to emulate market activity, normally to simulate fills against our test strategy's orders.  Many fill simulators, as found in the literature, are intended for testing long-term strategies with relatively few trades per day.  As a result, these simulators will typically assume orders are always filled, but at a volume and price that depends on factors like daily trade volume and average prices.  Market making strategies, however, will need to trade multiple times a day and will need to react to the current market as part of their strategy.  Our fill simulator will need to present more realistic market data \(e.g. five minute book snapshots\), and will need to simulate trades against something that looks like an actual order book.  The fill simulator we present here will, therefore, bear a closer resemblance to an order book simulator rather than a traditional fill simulator.

Our fill simulator will build an order book for each asset type by simulating the arrival of orders and trades.  The orders we simulate will include new orders, price changes, and cancellations.  The market data provided to our strategy will consist of the current order book maintained by our fill simulator; and, orders created by our strategy will be inserted into the same order book.  Our fill simulator will also simulate the arrival of trades.  These trades will be used to fill orders on the order book, regardless of whether these orders are simulated, or submitted by our strategy.  The random arrival of orders and trades will be implemented by a set of *generators* which are functions which create realistic market data based on the statistical properties of historic data, namely: arrival rate, order side, order size, and price.  We spend the remainder of this section describing how the simulated order book will operate.  We'll show how we derive generators in [Example 15](#example-15---modeling-orders-and-trades) below.  We'll then use our order and trade model in [Example 16](#example-16---testing-market-making-strategies).

A simulated order book for a given asset type sorts bid and ask orders by price with all orders at a given price further sorted first-in first-out according to arrival order.  This implies that incoming trades fill the oldest orders first at the best price.  An order book is modified by the following events:

* **New Order**: a new order will have properties: origin \(either "simulated" or "strategy"\), side, duration, volume, minimum volume, TOB \(simulated orders only\) and price \(strategy orders only\).  All orders are assigned a unique order ID when they are added to the system.  Orders with origin "strategy" will be inserted at the end of the queue at the appropriate price level on the appropriate side.  Orders with origin "simulated" will be handled as follows:
  1. If "TOB" is true, then the new order is automatically inserted at the top of book at the appropriate side.  The price of the order is set to be 0.01 ISK above the previous top of book.
  2. If "TOB" is false, then the position of the new order is randomly distributed among current orders \(using an exponential distribution, making it more likely that the order will appear towards the top of the book\).  The price of the order is set to be 0.01 ISK above the price of the order which appears immediately behind the new order.  If this is the first order on a side, then the price will be set at an offset from a reference price \(see below\).
* **Change Order**: a changed order will have properties: origin \(either "simulated" or "strategy"\), side, order ID \(strategy orders only\) and price \(strategy orders only\).  Orders with origin "simulated" will randomly update an existing simulated order by moving it to the top of the book \(the order to be updated is selected via an exponential distribution, making it more likely that the modified order is near the top of the book\).  Orders with origin "strategy" will update a previous order with the given order ID \(assuming the given order still exists\).  Note that the order management system will charge the strategy an order change fee, as well as any additional fees as required by EVE's trading rules.  Regardless of the source, if the price update "crosses the spread" \(i.e. exceeds the price of the best order on the other side of the book\), then a trade will occur against the appropriate matching order\(s\).  If any volume remains after the trade, then the order is left on the book at the new price level.
* **Cancel Order**: a cancel order will have properties: origin \(either "simulated" or "strategy"\), order ID \(strategy orders only\) and side.  Orders with origin "simulated" will randomly cancel a simulated order on the appropriate side of the book \(random selection is exponential, biased towards orders near the bottom of the book\).  Orders with origin "strategy" will cancel the order identified by the given order ID \(assuming the given order still exists\).
* **Trade**: a trade will have properties: side, and volume.  Trades will always match against the top of book on the given side.  Trades with volume above the available order volume on a given side will fill all orders, and will simply drop remaining volume.

The order management system will implement the usual trading fees and rules for EVE's markets, namely:

* Limit order placement fees:
  * A flat broker charge for limit orders
  * Sales tax on filled ask orders
* Order book views available to our strategy will be snapped at \(simulated\) five minute intervals.  This emulates the actual update frequency of EVE's markets for third party use.
* The usual EVE order rules apply, e.g. order actions can only occur every \(simulated\) five minutes, only price can be changed, price changes may incur additional fees, etc.

With this setup in place, we can execute a simulation as follows:

1. Compute a reference price for each asset under simulation.  This price can be the mid-point of the spread in the first snapshot on our simulated day.  When no orders are present on a side, we'll price new orders at an offset from the reference price.
2. Run the simulator for a preset *warmup* period in which random orders \(but no trades\) are generated and inserted into the appropriate order book.
3. Start the event simulator.  The strategy under test will execute as needed, although market data will only change once every five minutes as described above.  Order and trade events will arrive as determined by the appropriate generators.
4. Continue to run the simulation until the configured end time is reached.
5. Report results.

The degree to which our simulation emulates realistic trading depends on the properties of our random order and trade generators.  We take up the construction of generators in our next example.

### Example 15 - Modeling Orders and Trades

In this example, we'll demonstrate the construction of models which emulate EVE asset order books.  Over time, an order book is updated according to the arrival of new orders, the change or cancellation of existing orders, and the arrival of "immediate" orders which result in trades.  A model of an order book attempts to generate random occurrences of these events such that the behavior of the simulated order book closely emulates actual market behavior.

The accurate simulation of market behavior is a rich and varied topic which we won't cover in detail here.  Instead, we'll focus on implementing just enough behavior to create a reasonably predicative simulation of market making behavior.  We'll construct our order book model based on the statistical properties of historic orders and trades we extract from market data.  In particular, from historic order book snapshots, we can model the order event properties such as arrival rate, order side, and order size.  The models we build from this example will ultimately be used to construct simulations on the next example.  As with our other examples, you can follow along by downloading the [Jupyter Notebook](code/book/Example_15_Modeling_Orders_and_Trades.ipynb).

In this example, we'll build a model of the order book for Tritanium in the most active station in The Forge.  For simplicity, we'll build our model from a single day of market history.  A more realistic model would be constructed from multiple days of history.  We'll use the latter approach in the next example.

Our model requires that we extract orders and trades from a day of market data.  As in previous examples, we'll need to infer some trades \(e.g. complete fills versus cancels\).  We'll use the same approach where complete fills and order cancels are distinguished by order size.  To do that, we need to pull in market history to build an order size threshold:

![Load Market History](img/ex15_cell1.PNG)

Likewise, we need a day of order book data from which to build our model.  Since we're building a model for market making, which always occurs at a single station, we'll further constrain the book to just orders placed at the local station:

![Load Order Book Data](img/ex15_cell2.PNG)

In the next cell \(not shown\), we compute the volume threshold we'll use to distinguish complete fills from canceled orders.

The essence of our trading model is that it is based on historical observations of orders and trades.  To that end, we'll need to extract and track the arrival of orders and trades for each asset type across all book snapshots.  Note that we don't need price information for orders or trades as this is likely to change day to day and is not relevant for our simulation needs.  We do, however, need to extract a reference price and spread from the first order book snapshot.  These values are used to help prime simulated books with reasonable starting values.

We extract price, trade and order information using the `collect_book_changes` function.  This function is a variant of our earlier trade inference code, the main change being that we also extract new, changed and canceled order information.  The properties we extract are described in the text above.  For example, when we extract new orders we record the side, duration, volume, minimum volume and whether the new order became the new top of book.  We use this function in the next cell to extract price and order information for our sample day:

![Extract Price and Order Information](img/ex15_cell3.PNG)

Our goal is to build a model of Tritanium which can generate a reasonable set of random orders and trades which emulate actual trading.  To do this, we'll build a number of distributions which we can sample to generate random orders and trades.  We'll start by creating a generator to produce random trades.  A trade has three characteristics we need to model:

1. A side (either buy or sell);
2. An arrival offset (delay from current time when trade will arrive); and,
3. A volume

One might wonder why we're not also computing a trade price.  This is because we assume trades always fill the top of the book.  Therefore, trade price is determined by existing orders: once we compute the side where the trade falls, we can compute the trade price.

We'll start by creating a generator to produce random trade volume.  We *could* try to model trade volume in aggregate, but in reality it's likely that sell and buy volume have different distributions.  We can verify our intuition by looking at the distribution of buy and sell trades we inferred from our sample day:

![Buy Versus Sell Trade Volume](img/ex15_cell4.PNG)

There are more sell trades than buys which distorts the data, but there are also some clear differences in the distribution, especially in the tail.

How can we model the distribution of trade volume for our simulation?  Normally, we would attempt to match the shape of our distribution to a well known statistical distribution.  However, we don't have enough data to make that possible in this example.  Also, market data at this granularity \(i.e. very fine\) is notoriously difficult to map to simple distributions.  To work around this problem, we'll instead resort to a rough approximation using a distribution based on the cumulative distribution function \(CDF\) inferred from the raw sample data.  We can create a CDF using a histogram with cumulative sums across the buckets.  Taking the inverse of this CDF gives a function we can randomly sample to generate values from the data population.  This is a well known technique which we implement in the next cell.

![Sample Generator from Sample Data Distribution](img/ex15_cell5.PNG)

With our sample generator in hand, we can now create volume generators for sell and buy trade volume based on our sample data.  We do this in the next cell, then graph the results for comparison with the source data:

![Trade Volume Generators and Graphs](img/ex15_cell6.PNG)

Not surprisingly, samples drawn from our volume generators look very similar to plots of the original sample data.  We can apply the same technique to generate random trade inter-arrival times.  An inter-arrival sample is formed by computing the time difference between the arrival time of subsequent sample trades.  There is a catch, however, in that trade arrival times are always on five minute boundaries because we assign trade time based on snapshot time.  The subsequent inter-arrival times would Likewise be equally spaced which is not very realistic and easy to game by a trading strategy.  Therefore, we'll first skew the inter-arrival samples by adding a uniformly distributed value between zero and 300 seconds to each sample.  This skew will simulate trades arriving randomly in the interval between snapshots.  With this change, we're now ready to create our trade inter-arrival time generator:

![Trade Inter-Arrival Time Generator](img/ex15_cell7.PNG)

The final property we need to generate for trades is side \(e.g. buy or sell\).  Since there are only two sides, we can construct a much simpler generator based on the ratio of buys to sells.  We'll create a generic function here which we'll use elsewhere when we need a side generator.

![Trade Side Generator](img/ex15_cell8.PNG)

We can now assemble our individual property generators into a random trade generator.  We do this in the next cell, following by the an example invocation of the resulting function.

![Random Trade Generator](img/ex15_cell9.PNG)

We'll turn now to constructing generators for random orders. There are three order operations we need to simulate:

1. New order arriving
2. Order price change
3. Order cancellation

It's likely that order type \(i.e. new vs. change vs. cancel\) has an effect on the distributions which describe the properties of these orders.  Therefore, we'll model each order type separately.  We'll also make one additional simplification which is that we won't try to model order prices.  As described in the text, we'll instead price orders based on orders currently in the book, only using an explicit reference price when a side of the book is empty.  We'll explain how this affects each order type in the descriptions below.

Starting with new orders, we need to model the following properties:

* *side* - either buy or sell
* *duration* - the number of days for which the order will be active
* *inter-arrival time* - the time \(in seconds\) before the next order will arrive
* *minimum volume* - minimum volume that must be transacted on each trade
* *volume* - total volume to buy or sell
* *top of book* - True if the order entered the snapshot as the new best bid or ask

As discussed above, we've omitted a property for the new order price.  Instead, we'll determine price as follows \(this is also described in the book text\):

1. If the side of the book where the order will appear is empty, then the new order is priced at a small random offset from a reference price accounting for reference spread.
2. Else, if the order is marked "top of book", then the new order is always priced just better than the current best offer on the appropriate side.
3. Otherwise, the order is placed randomly among the appropriate side with the position determined by an exponential distribution favoring the top of the book.  The price of the new order is just better than the order which appears "behind" it in the book.

As with trades, we'll derive a generator for each of these properties, then assemble all generators into a function which generates new random orders:

![New Order Property Generators](img/ex15_cell10.PNG)

Note that we've created an order duration generator which constrains output to a specific set of values.  This was done to much EVE's rules for order duration.  Likewise, we've created a "top of book" generator which operates similar to a side generator in that it randomly generates one of two values based on a random value sampled against a ratio.  We can assemble our generators into a random new order generator:

![Random New Order Generators](img/ex15_cell11.PNG)

Generators for order changes and cancels will complete the model.  These order types require the following properties:

* *side* - the side of the book the order will affect
* *inter-arrival time* - the time in seconds until the next instance of this event type

For change orders, we once again omit specific price targets and instead handle these orders as follows:

1. If the side where the change will occur is empty, then the change order is silently discarded.
2. Otherwise, an order is selected randomly using an exponential distribution which favors the top of the book.  The selected order is immediately re-priced to the top of the book on the appropriate side.

Our handling of change orders is based on the intuition that, in an active market, most order changes will be for the purpose of capturing the top of the book.  Therefore, most changed orders should become the new best bid or ask.  For cancel orders, price is not relevant.  Instead, as described in the text, we'll randomly select an order to remove where the selection is exponentially distributed favoring the bottom of the appropriate side of the book.  Our intuition here is that in an active market, cancels are more likely to occur on orders well away from the top of book \(i.e. orders very unlikely to fill soon\).  In both cases, we construct inter-arrival samples based on snapshot time, which means we need to skew timestamps as we've done for trade samples.

The next two cells show the creation of our change and cancel order generators.  Note that these generators can share a single generic order generator function:

![Random Change and Cancel Order Generators](img/ex15_cell12.PNG)

Our last cell shows an example of invoking each of the order generators:

![Order Generator Invocation](img/ex15_cell13.PNG)

This completes our order book model for Tritanium.  We'll use the techniques we derived in this example to create random order and trade generators in our simple market making simulator.  We show this process in the next example.

### Example 16 - Testing Market Making Strategies

In this example, we'll create and test a simple market making strategy using the market making targets we discovered in [Example 14](#example-14---selecting-market-making-targets).  There are three basic steps we need to perform to test a strategy:

1. Prepare market data samples for the strategy.
2. Implement the strategy.
3. Initialize and run the simulator with our prepared market data and our strategy.

We'll work through each of these steps below.  We've already introduced the concept of market making simulation above.  In particular, we described the need for market data, order management and fill simulation components.  In this example, we'll make all these concepts concrete by introducing code to create and simulate an actual market making strategy.  We'll begin by describing the structure of our simulation code.

We test our market making strategies by implementing a simple [discrete-event simulator](https://en.wikipedia.org/wiki/Discrete_event_simulation).  In a discrete-event simulation, behavior is represented by a sequence of events which reflect activity such as trades, orders, the availability of new market data, etc.  Each event occurs at a specified virtual time, and events are processed in virtual time order.  Participants in the simulation typically wait for specific events to occur, which are then processed, often resulting in the generation of new events.  There are many open source simulation frameworks available online.  We've chosen to implement our simulation using [SimPy](https://simpy.readthedocs.io/), which is a Python framework that makes use of [generators](https://docs.python.org/3/glossary.html#term-generator) to implement processes which wait for, then process, simulation events.

We'll introduce the simulator's API by way of the following strategy, which buys and sells a single asset:

```python
from evekit.sim import MMSimOMS, MMOrderStatus, MMSimStrategyBase

class SimpleStrategy(MMSimStrategyBase):

    def __init__(self, oms, tax_rate, broker_rate, order_change_fee, type_id, units):
        super().__init__(oms, tax_rate, broker_rate, order_change_fee)
        self.type_id = type_id
        self.units = units

    def run(self, env):
        # Wait for the first market data for our asset type
        order_book = yield self.oms.order_book(self.type_id)

        # Place a buy order for an asset
        top_bid = self.best_bid(order_book)
        price = top_bid + 0.01 if top_bid is not None else 0.01
        buy_order = self.tracked_order(self.type_id, 30, True, price, self.units, 1)

        # Wait for our buy order to be filled
        yield buy_order.closed()
        if buy_order.status != MMOrderStatus.FILLED:
            # Something unexpected happened, exit
            raise Exception("Buy order in unexpected state: " + str(buy_order.status))

        # Place a sell order for the asset we just bought
        order_book = self.oms.get_current_order_book(self.type_id)
        top_ask = self.best_ask(order_book)
        price = top_ask - 0.01 if top_ask is not None else 1000000000
        sell_order = self.tracked_order(self.type_id, 30, False, price, self.units, 1)

        # Wait for our sell order to complete.  This is optional, the sell order
        # can be filled whether the strategy waits for it or not.
        yield sell_order.closed()
```

Our strategy class inherits from a base strategy class, `MMSimStrategyBase`, which is provided by the evekit framework.  The constructor for our strategy initializes the base strategy with a reference to the Order Management System \(OMS\), as well as various fees we'll need to charge to model actual trading.

The base class provides a few convenience functions:

* `best_bid(book)`, `best_ask(book)`: Given an order book, returns the current best bid or ask; or `None`, if a top of book does not exist on the given side.
* `tracked_order(type_id, duration, buy, price, volume, min_volume)`: Submits a new buy or sell order to the OMS which will be tracked by the base class.
* `promote_order(order, book, limit)`: Changes the price of an existing order so that it captures top of book on the appropriate side.  That is, the order is "promoted" to the top of book.  A limit can be set so that the price never exceeds a certain target.
* `order_dataframe`: Produces a Pandas DataFrame recording the current state of every tracked order, including any fees or proceeds.  We use this for post simulation analysis.
* `strategy_summary`: Produces a human readable summary of trading outcomes for the strategy.  This can also b eused for post simulation analysis.

The base class handles most interactions with the OMS.  However, we rely on the OMS directly for two functions:

* `order_book(type_id)`: Produces a simulation event which will be triggered when the next new order book is available for the given type.
* `get_current_order_book(type_id)`: Returns the current order book for the given type.

The object returned by `tracked_order` is an instance of `MMSimOrder` which has its own API:

* `gross`: Returns the gross proceeds of the order so far.  This will be positive for a sell order, and negative for a buy order.
* `net`: Returns the net proceeds of the order so far.  This is just gross less broker and sales tax fees as configured for the simulation.
* `closed`: Returns a SimPy `Event` that triggers when the order is closed \(for whatever reason\).
* `cancel`: Attempts to cancel the order.
* `change(price)`: Attempts to change the price of the order.  This will incur order change and possibly broker fees.

Note that order books are always delivered to the strategy as a Pandas DataFrame.

Now let's walk through the strategy line by line.  Strategy execution starts in the `run` method, which is passed a reference to the SimPy `Environment` for the current simulation:

```python
def run(self, env):
    # Wait for the first market data for our asset type
    order_book = yield self.oms.order_book(self.type_id)
```

Our first action is to wait for the next order book for the type we wish to trade.  The `order_book` method returns a SimPy `Event` which will trigger when the order book is available.  With SimPy, we `yield` an event to suspend the strategy until the event fires.  Therefore, our strategy code is now blocked until the next order book is available:

```python
    # Place a buy order for an asset
    top_bid = self.best_bid(order_book)
    price = top_bid + 0.01 if top_bid is not None else 0.01
    buy_order = self.tracked_order(self.type_id, 30, True, price, self.units, 1)

    # Wait for our buy order to be filled
    yield buy_order.closed()
    if buy_order.status != MMOrderStatus.FILLED:
        # Something unexpected happened, exit
        raise Exception("Buy order in unexpected state: " + str(buy_order.status))
```

When the next order book becomes available, we place a buy order for our chosen asset.  We use the `best_bid` method from the base class to ensure we price our buy order just above the current best bid.  The `buy_order` object is an instance of `MMSimOrder`, and will be tracked by the base class since we used the `tracked_order` method.  Order objects provide an event which triggers when the order has been closed.  We wait \(i.e. yield\) on this event, then verify that the order closed because it was filled.  The order could also expire or be canceled, but in this example we set the order duration to 30 days, and we do not cancel any orders.  Therefore, the order should only complete if it is filled.

```python
    # Place a sell order for the asset we just bought
    order_book = self.oms.get_current_order_book(self.type_id)
    top_ask = self.best_ask(order_book)
    price = top_ask - 0.01 if top_ask is not None else 1000000000
    sell_order = self.tracked_order(self.type_id, 30, False, price, self.units, 1)

    # Wait for our sell order to complete.  This is optional, the sell order
    # can be filled whether the strategy waits for it or not.
    yield sell_order.closed()
```

When our buy order completes, we request the current order book in preparation for placing a sell order.  As with the buy order, we use the order book to price our sell order just ahead of the current best ask.  We end the strategy by waiting for our sell order to complete.  This is not strictly necessary as the order will complete \(assuming a matching trade\) whether we wait for it or not.  Once the order completes, our strategy will cease execution although the simulator may continue running depending on our configured end time.

This example strategy is not very sophisticated and in fact may not even trade since prices are never adjusted once orders are placed.  We'll implement a slightly more interesting strategy later in this example.

Now that we've had a taste of what a strategy looks like, let's move on to configuring and executing a simulation of a more interesting strategy.  As with our other examples, you can follow along by downloading the [Jupyter Notebook](code/book/Example_16_Testing_Market_Making_Strategies.ipynb).

For this example, we'll need to bring in our market maker simulation library code.  This has been added to the first cell for this example \(not shown\).  We'll build a strategy which makes a market for the eight asset types we discovered in [Example 14](#example-14---selecting-market-making-targets).  The analysis which produced these assets was conducted in the busiest station in The Forge, so we'll use the same environment for our simulation:

![Simulation Environment Setup](img/ex16_cell1.PNG)

Note that we've also set the date range the same as in Example 14 \(i.e. every Saturday over a four month period\).  This is because our first step will be to generate raw market data from which we'll build our order book models.  To populate our models, we'll follow the same steps as in [Example 15](#example-15---modeling-orders-and-trades), which starts with loading market history for use in order and trade inference:

![Market History for Trade Inference](img/ex16_cell2.PNG)

Followed by computing volume thresholds which will allow our order and trade collector to distinguish large trades from cancel orders:

![Large Order Threshold Computation](img/ex16_cell3.PNG)

The next cell \(not shown\) contains the same order extractor we used in Example 15.  We use this code to extract orders for each market making type in each day in our date range:

![Extract Target Orders and Trades](img/ex16_cell4.PNG)

When this cell completes, we are left with a map from asset type to a list of collected order information for each day in our date range.  The simulator builds order book models from input we supply in the form of a map from asset type to an object containing:

* a *reference price* which is used as a basis for pricing simulated orders added to an empty order book side;
* a *reference spread* which is used to position orders relative to the *reference price* when an order book side is empty;
* a list of *orders* representing new, re-priced or canceled orders; and,
* a list of *trades*.

To provide data in this format, we need to aggregate the data we extracted from each day in our date range.  The next cell shows this aggregation:

![Aggregating Model Input Date](img/ex16_cell5.PNG)

namely:

* the *reference price* is computed as the average reference price across all extracted days;
* the *reference spread* is computed as the average reference spread across all extracted days;
* the list of *orders* is the aggregate of all extracted orders, with timestamps adjusted to eliminate the week gap between extracted days; and,
* the list of *trades* is the aggregate of all extracted trades, with timestamps adjusted in the same manner.

We'll use this data further below when we execute our simulation.

The example strategy we created above was illustrative, but would not be a very effective market making strategy.  We'll now create a more interesting strategy and analyze its performance below.  Our strategy will alternate between buying and selling a fixed number of units of an asset.  The strategy will continue this pattern until the simulation ends.  While an outstanding order is out, the strategy will monitor the price of the order relative to the book and re-price the order as needed to regularly capture the top of the book.  This will ensure that the strategy will trade regularly as long as there is not too much market competition.  In all cases, the strategy will only have one order outstanding at any given time: either a buy or a sell.  We'll review the code in parts as in the previous example.

Our strategy is initialized as before with information needed for the base strategy, as well as the asset type we'd like to trade, and the number of units we should buy or sell at any given time:

```python
class RoundTripStrategy(MMSimStrategyBase):

    def __init__(self, oms, tax_rate, broker_rate, order_change_fee, type_id, units, verbose=False):
        super().__init__(oms, tax_rate, broker_rate, order_change_fee)
        self.type_id = type_id
        self.units = units
        self.verbose = verbose
```

As in the previous strategy, execution starts in the `run` method which accepts a reference to the current SimPy `Environment`.  There's little point entering a market until the ratio between the best bid and ask become profitable.  Therefore, this strategy computes the minimum ratio and waits until an order book arrives in which the best bid and ask meet the profitability threshold:

```python
    def run(self, env):
        # Save the appropriate price ratio we need before we should enter a round of market making.
        # This is just the formula described in the text.
        #
        price_ratio_target = (1 + self.broker_rate) / (1 - self.tax_rate - self.broker_rate)
        try:
            while True:
                #
                # Wait for the first snapshot with a profitable spread ratio.
                #
                buy_order = None
                while buy_order is None:
                    order_book = yield self.oms.order_book(self.type_id)
                    top_bid = self.best_bid(order_book)
                    top_ask = self.best_ask(order_book)
                    if top_bid is None or top_ask is None:
                        # Spread not available
                        continue
                    if top_ask / top_bid <= price_ratio_target:
                        # Spread not profitable
                        continue
```

When the spread turns profitable, we place a buy order priced just above the current best bid:

```python
                    price = top_bid + 0.01 if top_bid is not None else 0.01
                    buy_order = self.tracked_order(self.type_id, 30, True, price, self.units, 1)
                    if self.verbose:
                        print(str(env.now) + " Buy order placed at " + str(price))
```

The strategy now turns to waiting until our buy order has been completely filled.  However, unlike the previous strategy, we will continue to monitor the current order book to ensure we always capture the best bid.  SimPy overrides the bit-wise disjunctive operator to allow our strategy to wait either until our order is closed, or until a new market snapshot is created:

```python
                #
                # Wait for buy order to be filled, making sure we always capture the best bid.
                # When the order is filled, turn around and post a sale.
                #
                sell_order = None
                c1, c2 = buy_order.closed(), self.oms.order_book(self.type_id)
                while sell_order is None:
                    result = yield c1 | c2
```

When `result` fires, it will return a map with a key for each of the events which triggered.  The values in the map correspond to the values returned by the triggered events.  If the buy order completes, then we're ready to place a sell order.  Note that we first compute a minimum price to protect re-pricing our sell order below profitability.  This price is determined by the spread profitability ratio and the price at which the asset was purchased \(see above\).  We place the sell order with a price designed to capture the best ask, while not going lower than the minimum sell price.  Note that creating the sell order also breaks us out of the loop above:

```python
                    # Check for order status change first to avoid racing with new order book
                    if c1 in result:
                        # Order closed, if it was filled then place our sell order
                        if buy_order.status != MMOrderStatus.FILLED:
                            # Something unexpected happened, exit sim
                            raise Exception("Buy order in unexpected state: " + str(buy_order.status))
                        if self.verbose:
                            print(str(env.now) + " Buy order completed")
                        # The final price of our buy order gives us the minimum price for which we
                        # must sell the assets.  This equation is also described in the text.
                        minimum_sell_price = buy_order.price * (1 + self.broker_rate) / \
                                                               (1 - self.tax_rate - self.broker_rate)
                        order_book = self.oms.get_current_order_book(self.type_id)
                        top_ask = self.best_ask(order_book)
                        price = top_ask - 0.01 if top_ask is not None else 1000000000
                        price = max(price, minimum_sell_price)
                        sell_order = self.tracked_order(self.type_id, 30, False, price, self.units, 1)
                        if self.verbose:
                            print(str(env.now) + " Sell order placed at " + str(price))
```

If a new order book arrives while we're waiting for our buy order to complete, then we'll verify that our buy order still captures the best bid.  The `promote_order` function in the base strategy handles this automatically, only re-pricing if we're no longer at the top of the book.  Note that there's no check to ensure we don't price ourselves out of profitability.  We leave that improvement as an exercise for the reader:

```python
                    if c2 in result and sell_order is None:
                        # Make sure we still own the best bid
                        order_book = result[c2]
                        new_price = self.promote_order(buy_order, order_book)
                        if self.verbose and new_price is not None:
                            print(str(env.now) + " Buy order price changed to " + str(new_price))
                        # Reset for next order book
                        c2 = self.oms.order_book(self.type_id)
```

We wait for our sell order to complete in the same way that we waited for our buy order to complete.  If the sell order completes first, then we'll break out of the loop:

```python
                #
                # Wait for sell order to be filled, making sure we always capture best ask.
                #
                c1, c2 = sell_order.closed(), self.oms.order_book(self.type_id)
                while True:
                    result = yield c1 | c2
                    # Check for order status change first to avoid racing with new order book
                    if c1 in result:
                        if sell_order.status != MMOrderStatus.FILLED:
                            # Something unexpected happened, exit sim
                            raise Exception("Sell order in unexpected state: " + str(sell_order.status))
                        # Done, exit strategy
                        if self.verbose:
                            print(str(env.now) + " Sell order completed")
                        break
```

If we receive a new order book, then we'll verify that our sell order still captures the top of book.  However, this time we impose a `side_limit` to avoid moving our sell order out of profitability:

```python
                    if c2 in result and sell_order.status == MMOrderStatus.OPEN:
                        # Make sure we still own the best ask
                        order_book = result[c2]
                        new_price = self.promote_order(sell_order, order_book, side_limit=minimum_sell_price)
                        if self.verbose and new_price is not None:
                            print(str(env.now) + " Sell order price changed to " + str(new_price))
                        # Reset for next order book
                        c2 = self.oms.order_book(self.type_id)
```

Once our sell order completes, we'll loop around and repeat the process.  As a matter of convenience, we have surrounded our strategy code with a `try`-`catch` block which catches SimPy interrupts, halting the strategy when this occurs.  We'll use this mechanism when we extend this strategy later in the example:

```python
        except simpy.Interrupt:
            # allow us to be interrupted, we just stop when this happens
            pass
```

You'll find the code for this strategy in a cell in the example Jupyter notebook.

Now that we've prepared model data and implemented a test strategy, we're finally ready to simulate.  The next cell runs our first simulation:

![Our First Simulation](img/ex16_cell6.PNG)

Our simulator requires that we define constants for the sales tax rate, the broker rate for limit orders, and the fee charged for re-pricing an order \(not including any additional broker fees, which are charged automatically\).  We also need to pick a random seed to initialize the random order and trade generators.  You'll normally want to run your simulations multiple times with different seeds, but for this first run we'll choose a single seed.  Every simulation we run has four steps:

1. Create the SimPy `Environment`;
2. Create and initialize the OMS with market data, constants and the random seed;
3. Create and start the strategy to test; and, finally,
4. Run the simulation, normally including a stop time.

Creating the environment and initializing the OMS are straightforward.  Note that we've passed in the market data map we created earlier in the example.  Creating and initializing the strategy under test is implementation dependent but normally includes passing the arguments required by the base strategy \(i.e. OMS reference, sales tax, broker fee, and change fee\).  In this example, our strategy also requires the asset type to trade, the number of units to trade in each round, and \(optionally\) whether we want verbose output.  For this example, we're only trading the first asset in our market making target list; we've chosen an arbitrary value of 10 units per round; and, we've asked for verbose output to demonstrate the operation of the strategy.

After initializing your strategy, you must "start" it which, in SimPy terms, means calling the `process` function with the result of running your strategy's main execution method.  The behavior here is a bit subtle.  Normally, when your strategy's execution method is called, it will yield on the first event it will wait for.  This event then becomes the argument to the `process` function which ensures your execution method will resume when the event fires.  This behavior continues until your execution method exits without yielding an event.  You can spawn as many processes as you like and, in fact, we'll use this approach later when we trade all of our target market making assets.  But for now, we just need one process trading one asset type.

Calling the `run` method on the SimPy `Environment` will start the simulation, which is to say the generation, scheduling and dispatch of discrete events.  The `run` method will accept an `until` argument which specifies the simulated time at which the simulation should end.  Time values are arbitrary and can be interpreted however you like.  In our simulations, simulation time is expressed in seconds.  For example, new market snapshots will be generated every 300 simulation time units \(i.e. every 300 seconds or five minutes\).

Setting `verbose` to `True`, causes the actions of our strategy to be echoed in the output of the cell:

![Our First Simulation in Action](img/ex16_cell7.PNG)

The first value in each row is the simulated time when the action occurred.  From the output, we see that our first buy order was filled after an hour of trading with several price adjustments needed.  Our sell order required even more time to fill at approximately three hours with multiple price changes required.  Our simulation ends with an open sell order \(more on this below\).

The print statements we added to the end of our simulation code cause the following summaries to be displayed when the simulation completes:

![First Simulation Summary](img/ex16_cell8.PNG)

The OMS trading summary reports the number of trades, total volume, and pricing performance for each asset type we simulated.  Although our strategy only traded one asset type, the simulator dutifully simulated all eight assets we provided data for, so there are eight rows.  The OMS summary is useful for spot checking whether our strategy captured expected volume from the overall market.  In this particular run, excluding the open sell order at the end, we captured about a third of the total daily volume for the first asset.  The base strategy also provides a summary method which we display after the OMS summary.  The base strategy summary replays our strategy's trade activity, showing the final disposition of every tracked order placed by our strategy, including a running sum of the strategy profit and loss \(PNL\).  In terms of performance, our strategy ended the day with an open sell order.  If we backtrack to the last completed sell order, we show a total PNL of about 3.7M ISK \(we'll discuss how to report around open orders below\).  It's interesting to note that in an entire day of trading, our strategy only traded a volume of 100 units \(50 bought, and 50 sold\), excluding the last buy and open sell.  These results may be an outlier, or they may be typical.  The only way to know for sure is to run more simulations with different random seeds to see if the results are different.  We'll do this momentarily.

When running a large number of simulations, it is often desirable to aggregate performance results so that we can compute performance across all runs.  For this reason, the base strategy also provides the performance summary in the form of a Pandas DataFrame:

![Performance Summary DataFrame](img/ex16_cell9.PNG)

This DataFrame is indexed by simulation time and provides separate columns for all fees and proceeds for each order.  In this particular example, the DataFrame view also shows that our last sell order was partially filled.  The DataFrame does *not* compute running PNL.  Instead, we must add the appropriate columns manually.  This is a simple operation on a DataFame, e.g.:

```python
(strategy_df.gross - strategy_df.tax - strategy_df.broker_fee).sum()
```

However, one problem with this simple expression is that it includes the results of our partially filled sell order.  Some simulations will complete with no open positions, whereas others \(like the current example\) will complete with one or more open orders.  In order to normalize over these results, we will compute PNL with a simple function that excludes any open sell orders:

![Normalized PNL Computation](img/ex16_cell10.PNG)

We're now ready to analyze our strategy over multiple simulations.  We'll generate 100 random seeds and run the same simulation using each seed.  The next two cells \(not shown\) perform this computation.  We can then aggregate our results across all runs:

![Aggregated Simulation Results](img/ex16_cell11.PNG)

Our span of 100 runs shows a wide range in performance.  The mean and median are reasonably close which suggests a well behaved distribution of results.  The standard deviation is rather large suggesting high variance around the mean.  Of course, we can simply build a histogram of the data to see if the shape matches our intuition:

![Distribution of Simulation PNL](img/ex16_cell12.PNG)

This shape suggests a slightly exponential distribution which would allow further predicative analysis given more simulation runs.  We'll leave such analysis as an exercise to the reader.

You may recall that our strategy accepts both the asset type to trade, as well as the unit size of our orders.  We arbitrarily set unit size to 10 for our first run.  Does unit size affect the performance of our strategy?  We've reasoned before that for a typical active asset, we might expect to capture 10% of the total market volume for ourselves.  Should we set unit size to 10% of the typical volume?  Given that we'd like our strategy to make multiple buy/sell round trips, that value is probably too large.  We might therefore shrink the unit size another 10% which would allow for roughly 10 market making round trips in a typical trading session.  In other words, we might estimate a reasonable unit size to be 1% of total volume for a target asset.  We can compute unit size based on the raw trade data we use to parameterize the simulation:

![Estimating Appropriate Unit Size](img/ex16_cell13.PNG)

How well does this choice work?  This is something we can easily evaluate by simulation.  We'll simulate the same asset type as above but with three different unit sizes:

1. One half of our estimated unit size \(i.e. 1% times 0.5 or 0.5% of the average trade volume\);
2. Exactly our estimate unit size; and,
3. One and half times our estimated unit size \(i.e. 1% times 1.5 or 1.5% of average trade voume\).

We'll perform 100 runs of each size using the same set of randomly generated seeds for each run.  Let's take a look at the results:

![Unit Size Simulation Results](img/ex16_cell14.PNG)

In this example, 1% of average trade volume for the first asset type is 13 units, representing the middle row of results.  In general, larger order sizes produce larger average results, with apparently diminishing returns above our initial guess at the ideal unit size.  A case could be made for using a slightly larger unit size, but for this example we'll stick with our rough estimate of 1% of total volume.

So far, we've focused on trading a single asset.  Let's turn now to trading all eight of our market making targets.  A simple way to trade multiple asset types is to create a separate instance of our strategy for each type.  Each instance must be initialized and started in a process separately.  We'll once again run our simulation 100 times, then aggregate the results.  The following cell shows the construction of the simulation:

![Trading All Assets](img/ex16_cell15.PNG)

Let's look at the results:

![All Asset Simulation Results](img/ex16_cell16.PNG)

Once again, we see a wide range of results with a high standard deviation.  Nonetheless, many players would be happy to obtain the average result in each market making session.

The results we've shown so far represent an entire day of trading.  Most players, however, will not spend an entire day managing orders and making markets.  Therefore, we may wish to constrain our strategy so that trading only occurs during a subset of the day.  Results from a "time block" of trading are more likely to represent our actual results.  A second, slightly more technical, issue is that we've always started our strategy at the beginning of simulated time.  Although the simulator "warms up" the book by pre-populating orders, it does not simulate any trades until the simulation actually starts.  To make the simulation more realistic, we should allow the simulator to run for a \(simulated\) hour or so in order to give the book a chance to move to a more realistic state.  We consider both of these issues as we finish our analysis of market making simulation.

To allow for a delayed start, and to simulate a block of trading, we'll implement an extension of our existing trading strategy which sleeps until a designated start time, and trades until a dedicated stop time.  We'll arbitrarily choose to trade a four hour block starting one hour after the start of the simulation.  It is tempting to consider starting our strategy earlier or later to simulate trading at different times of the day.  However, our simulation as constructed has no concept of time of day, so such variants would likely not produce representative results.  A more realistic simulation would need to construct an order book model which incorporates time of day.  We leave that topic for future work.

We can implement a delayed-start block-time strategy as a simple subclass of our original strategy:

```python
class DelayedBlockRoundTripStrategy(RoundTripStrategy):

    def __init__(self, start_time, end_time, oms, tax_rate, broker_rate, order_change_fee,
                 type_id, units, verbose=False):
        super().__init__(oms, tax_rate, broker_rate, order_change_fee, type_id, units, verbose)
        self.start_time = start_time
        self.end_time = end_time

    def run(self, env):
        # Wait until our start time
        yield env.timeout(self.start_time - env.now)
        if self.verbose:
            print(str(env.now) + " strategy starting")

        # Now launch the strategy and interrupt when the end time occurs
        stop_strategy = env.timeout(self.end_time - env.now)
        run_strategy = env.process(super().run(env))
        yield stop_strategy | run_strategy
        if not run_strategy.triggered:
            # Interrupt
            run_strategy.interrupt()
        if self.verbose:
            print(str(env.now) + " strategy stopped")
```

Our derived strategy has the same initialization as the original strategy, but also accepts a start and stop time in seconds.  The main execution loop yields a timeout event which waits until the designated start time.  When this time is reached, we create two events:

1. A timer event representing the stop time; and,
2. An instance of our original strategy started in a SimPy `process`.

In SimPy, a `process` is also a type of event which we can wait on.  Thus, we wait on either our original strategy completing, or the expiration of the stop timer.  If the stop timer expires first, then we'll send an interrupt to our strategy process which causes it to stop trading \(recall the try-catch block in our original strategy\).

We can now simulate the performance of our strategy over a block of time.  For this example, we'll choose to start the strategy one hour \(simulated time\) into the simulation, and end four hours later.  As in previous examples, we'll perform 100 separate runs and aggregate the results:

![Four Hour Block Simulation Results](img/ex16_cell17.PNG)

Over a four hour block, average trends slightly higher than the median but the standard deviation is quite large.  There are also some extreme runs with at least one run generating no profit.  You can vary the trading block size but note that smaller blocks will give your strategy very few opportunities to find and make good trades.  Another variant, is to leave any open sell orders open for the remainder of the day \(which you can do by continuing to run the simulation well beyond when the strategy stops\).  This reflects what you'd likely do in actual trading: if you ended the day with open sell orders, you'd likely just leave them open on the off chance they would be filled later.

We've only scratched the surface of market making strategy construction and simulation.  For example, we could place sell orders as soon as we have any assets to trade, instead of waiting for our buy order to complete first.  We leave these variants, as an exercise for the reader.

## Introduction to Risk management

  * managing risk (bought items waiting to be sold)
    * how long should I hold unsold assets?
  * Example 17 - simple risk projection

## Strategy Effectiveness
* strategy effectiveness
  * pros:
    * Easy to execute once you've chosen your targets
    * Cheap, can start small
  * cons:
    * Highly competitive, many 0.01 ISK games
    * Volume game, need to play a lot to make a lot

## Variants
* variants
  * relisting
    * buy out all current sellers
    * re-list well above the last best ask to attempt to profit
    * probably ideal for an unbalanced side (e.g. mostly buyers) as long as there is not too much competition
  * Example 18 - relisting
  * cyclical market making
    * look for ask cycles, buy at low end of cycle and resell
    * OR: look for bid cycles, bid at low end of cycle and resell
  * Example 19 - finding bid and ask cycles

## Practical Trading Tips
* practical trading tips
  * Multi-day positions require risk management
  * order layering to stay at the top of the book
  * pricing tricks - 1.01 increases to catch sloppy competitors
