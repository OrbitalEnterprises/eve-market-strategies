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
* $s_t$ - station sales tax
* $b$ - station broker fee

the total profit, $r$, obtained by making a market for a given asset type is:

$r = p_a \times n - p_a \times s_t \times n - p_a \times b \times n - p_b \times b \times n - p_b \times n$

where the first term is the gross profit, and the remaining terms reflect sales tax, broker fees for placing limit orders, and the cost of buying assets at the best bid.  A market making transaction is profitable when $r > 0$. That is, when:

$p_a \times n - p_a \times s_t \times n - p_a \times b \times n - p_b \times b \times n - p_b \times n > 0$

or, by re-arranging terms:

${p_a \over p_b} > {{1 + b}\over{1 - t - b}}$

This last expression gives us a simple test to determine whether an asset is currently profitable for market making \(the terms on the right are all constant\).

If an asset is profitable for market making, then we'd also like to determine the expected return for this strategy.  From the last chapter, we know that return is ${{gross}\over{cost}} - 1$.  Given the same definitions above, the expected return is therefore:

${{p_a}\over{p_a \times s_t + b \times (p_a + p_b) + p_b}} - 1$

Beyond profitability, this last expression allows us to filter for market making opportunities which exceed a certain return.

Active market making in EVE has two important limitations which must also be taken into consideration:

* The price of an order can be changed without canceling the order \(which incurs a fee, see below\).
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

![Market Making Liquidity Filter](img/ch3_fig1.PNG)

For market making, we'll test for assets which trade for a minimum number of days, and have a minimum number of orders each day.  For this example, we'll filter across 30 days of market history leading up to our target date.  We'll require at least 500 orders for each trading day as well.  Given these constraints, we can then filter for liquid assets:

![Liquid Asset Filter Results](img/ch3_fig2.PNG)

Our results show about 100 assets which meet our criteria.  You can change these criteria as needed for your own trading.  Note, however, that admitting more assets will increase analysis time and likely require more memory.

Now that we have our target assets, we're ready to load order book data for our target date.  Since we're analyzing market making specifically, we can filter the book down to just those orders placed at our target station:

![Order Book for Market Making](img/ch3_fig3.PNG)

Our first task is to determine which assets have the most active bid and ask orders.  Frequent changes to the best bid or ask show competition in the market.  We can compute change frequency simply by checking for changes to the best bid or ask between order book snapshots.  We'll define three simple functions to compute best bids, best asks, and to check whether orders are identical.  For the purposes of market activity, the best bid or ask has changed if a new order has replaced the previous order, or if the price has changed:

![Best Bid, Best Ask and Order Equivalence Check](img/ch3_fig4.PNG)

We can then compute change frequency for each type by tabulating best bid/ask changes between snapshots.  The following function performs this calculation and returns a Pandas DataFrame with the change time for every asset:

![Function to Compute Best Bid/Ask Changes](img/ch3_fig5.PNG)

The next two cells invoke this function on the order book over our liquid assets.  We can view the most active assets by counting the number of times each asset changes.  Let's take a look at the top 10 results:

![Top 10 Most Active Assets](img/ch3_fig6.PNG)

You may recall there are 288 order book snapshots in a day.  None of our liquid assets has a change count equal to this value, so we know none of these assets change every snapshot.  However, there are 23 assets which changed more than 144 times, or once every other snapshot \(on average\).  There are almost certainly active market makers trading on these assets.

An asset which changes more than 48 times is, on average, changing every 30 minutes.  All but 13 of our asset list meet this criteria.  However, as we lower the change frequency, it becomes more likely that changes may be grouped together over a smaller time period.  There are at least two ways we can improve our intuition around the spacing of changes for an asset:

1. We can plot the times when changes occurred; and,
2. We can look for clusters in the data showing times when there were frequent changes.

As an example, let's look at "Conductive Polymer" which changed 63 times on our target day.  The following plot shows the time of each change during the trading day:

![Best Bid/Ask Changes for Conductive Polymer](img/ch3_fig7.PNG)

The plot shows an obvious gap of about two hours at mid day.  Also, there appear to be clusters of trades and certain times of day.  One way to better understand clustering effects is to resample the data and count the number of bid/ask changes in each re-sampled interval.  This is also a way to determine the most active times of day for a given asset.  The next cell computes cluster size for three different re-sampling frequencies:

![Change Clusters for Conductive Polymer at 60, 30 and 15 minutes](img/ch3_fig8.PNG)

The mid day gap is very obvious in the 15 minute re-sampled data.  Conversely, the 60 minute sampled data shows the most active times of day (at about 05:00, 17:00 and 20:00).  As you might expect, active times are most relevant for less active instruments.  Very active assets show no real gaps.  To see this, we can look at the plot of changes for "Prototype Cloaking Device I", the most active asset on our list:

![Best Bid/Ask Changes for Prototype Cloaking Device I](img/ch3_fig9.PNG)

Astute readers may have noticed that both Conductive Polymers and Prototype Cloaking Devices show a very similar gap around 12:00 UTC.  This time range corresponds to daily downtime for EVE when no trading can occur.  Although down time is typically less than 30 minutes, trading on most assets consistently lags around this time.

From this example, it seems that counting best bid/ask changes is a simple way to identify likely market making candidates.  Let us turn now to estimating how many players are actively making a market for a given asset.

One way to identify an active market maker is to look for an order which changes frequently throughout the day.  Such orders will have the same order ID, but will change price one or more times as the owning player attempts to capture the best bid or ask.  If we simply counted the number of orders which change throughout the day, we'd likely have an overestimation of the number of active market participants because different players may participate at different times of the day.  Instead, we'll re-sample the order book over a configurable interval and tabulate the number of orders which change in a given interval.  This is still an estimate because some market participants may change their orders less frequently than our re-sampling interval.  However, results should be reasonable given a sufficiently large re-sampling interval.

A function to compute the number of orders changing for each type in a sampling interval is just a slight variant of our function for counting best bid/ask changes:

![Function to Count Changing Orders per Interval](img/ch3_fig10.PNG)

The result of this function is a Pandas DataFrame which gives the number of orders which changed at least once in a given resampling interval.  Let's look again at Conductive Polymers to see what this data looks like for an infrequently traded asset.  To provide more context, we'll overlay a plot of the change count data we computed above, resampled to the same interval we used for market participants.  Here's the plot for Conductive Polymers:

![Conductive Polymers Participants (bar - left axis) vs. Best Bid/Ask Changes (line - right axis) (1 hour samples)](img/ch3_fig11.PNG)

The peaks in the graphs do not quite line up and the sampled participant count is quite low.  One conclusion we might draw from this data is that market making is not really happening for Conductive Polymer.  Another possible conclusion is that the change cycle is much slower than one hour.  We can check out intuition by resampling for a larger change interval.  Here's the same plot for Conductive Polymer re-sampled over two hour intervals:

![Conductive Polymers Participants (bar - left axis) vs. Best Bid/Ask Changes (line - right axis) (2 hour samples)](img/ch3_fig12.PNG)

Changing the sample interval has not captured more market participants which reinforces the hypothesis that market making is probably not occuring on this asset.  Instead, this could be one large order competing with a regular flow of small orders placed by casual players throughout the day.  The owner of the large order must regularly re-position to capture the best bid or ask.  We can confirm our hypothesis by looking more carefully at the order book snapshots for the day.  We leave that task as an exercise for the reader.

What do participants look like for a more actively traded asset?  Let's look at the same plot for Prototype Cloaking Device I, sampled at one hour intervals:

![Prototype Cloaking Device I Participants (bar - left axis) vs. Best Bid/Ask Changes (line - right axis) (1 hour samples)](img/ch3_fig13.PNG)

From this plot, we see that there may be as many as 14 active market participants in a given hour of trading for this asset.  That's a lot of competition!  If we decide to trade this asset, we likely won't be successful if we plan on updating our prices once an hour.  What if we update our orders every 30 minutes?  We'll finish this example by looking at the sample plot sampled at 30 minute intervals:

![Prototype Cloaking Device I Participants (bar - left axis) vs. Best Bid/Ask Changes (line - right axis) (30 minute samples)](img/ch3_fig14.PNG)

The number of participants per interval has gone down by 30-50% in most cases, but is still quite large in some intervals.  It seems unlikely that you'll get away with updating your orders once every 30 minutes in this asset type.  If you want to trade this asset successfully, you'll likely need to be watching it all day \(more on this later\).

In this example, we've introduced a simple filter for finding asset types for which markets are likely being made.  We've also created a simple technique to estimate the number of participants making a market in a given type.  Note, however, that we've restricted our analysis to a single day, so the usual caveats apply.  A more proper analysis would consider active assets over a larger time range.  We'll discuss back testing later in this chapter.

## Elements of a Market Making Strategy
* Elements of a market making strategy
** which assets to trade?
*** liquid assets
*** spreads must be profitable
*** trade volume reasonable balanced between bid and ask
*** how much competition do we want?
*** how often can we change our orders?
** Example 14 - finding market making targets
** how can I test my strategy?
*** modeling order books and fills
** Example 15 - modeling order books and trades
*** simple backtest against model
** Example 16 - backtest a sample strategy
** managing risk (bought items waiting to be sold)
*** how long should I hold unsold assets?
** Example 17 - simple risk projection

## Strategy Effectiveness
* strategy effectiveness
** pros:
*** Easy to execute once you've chosen your targets
*** Cheap, can start small
** cons:
*** Highly competitive, many 0.01 ISK games
*** Volume game, need to play a lot to make a lot

## Variants
* variants
** luring the ask down
*** find agressive ask side
*** buy a few items
*** continually 0.01 ISK sellers to draw ask price down
*** buy out sellers and place ask
** Example 18 - finding competitive ask candidates
** cyclical market making
*** look for ask cycles, buy at low end of cycle and resell
*** OR: look for bid cycles, bid at low end of cycle and resell
** Example 19 - finding bid and ask cycles

## Practical Trading Tips
* practical trading tips
** tools almost mandatory - fortunately there are many available
** Multi-day positions require risk management
** order layering to stay at the top of the book
