# Market Making \(Station Trading\)

In real-world markets, a market maker is a market participant that maintains an inventory of assets \(e.g. stock\) so that they are able to buy or sell assets to other market participants as required.  Market makers help keep real-world markets running efficiently by providing *liquidity*, which is the ability to readily trade assets at stable prices.  Real-world market makers are compensated for the risk they take in maintaining an inventory of assets.  In some markets, this compensation takes the form of rebates offered to market participants willing to provide liquidity.  In most markets, however, market makers profit by maintaining a *spread* which is the difference in price between the current best bid and best ask.  A market maker can buy assets at the best bid \(assuming a willing counterparty\), then turn around and sell those assets at the best ask, pocketing the *spread* \(or vice versa for selling at the ask and buying at the bid\).  As long as the spread is greater than associated trading fees, the market maker will make a profit.  Note, however, that profit margins are typically very thin.  In real world markets, market making is a volume game.

EVE markets do not have sponsored market makers like real-world markets.  However, many players perform a similar function and profit in a similar fashion.  These players are referred to as "station traders" because they typically never leave the station they are trading in: all assets are bought and sold in the same station.  For all intents and purposes, however, station traders are really market makers: they compete with other players to have the best bid or ask, and they profit when they can buy assets at the best bid and re-sell those assets at the best ask \(or vice-versa\).  Besides hauling, market making is one of the most popular occupations for players pursuing a market trader play style.  Part of market making's popularity stems from the fact that little capital is required to get started.  To wit, there are numerous online videos explaining how to make quick ISK by market making.

In this chapter, we'll analyze market making as a market strategy in EVE.  We'll discuss the basics of profitability, and then work through the discovery of which assets provide good market making opportunities.  As market making is a time consuming activity, we'll also attempt to estimate how frequently you'll need to monitor your orders.  Less active players may want to use the results from this section to choose market making opportunities which fit better with their play styles.  We'll also talk briefly about market risk as this is the most significant risk factor for market making.  As in earlier chapters, we provide several examples illustrating how we derive opportunities and predict outcomes.  We conclude this chapter with a brief discussion of variants and practical trading tips.

## Market Making Basics

A simple EVE market making strategy first buys assets at the best bid, then sells these assets at the best ask.  All trading occurs within a single station.  Limit orders are placed for both the bid and ask \(incurring broker fees\), and sales tax is charged when ask orders are filled.

Given the following definitions:

* $p_a$ - the best ask price for an asset
* $p_b$ - the best bid price for an asset
* $n$ - the number of assets bought and sold
* $s_t$ - station sales tax
* $b$ - station broker fee
* $r$ - total profit of the transaction

the profitability of market making for a given asset type is:

$r = p_a \times n - p_a \times s_t \times n - p_a \times b \times n - p_b \times b \times n - p_b \times n$

where the first term is the gross profit, and the remaining terms reflect sales tax, broker fees for placing limit orders, and the cost of buying assets at the best bid.  A market making transaction is profitable when $r > 0$. That is, when:

$p_a \times n - p_a \times s_t \times n - p_a \times b \times n - p_b \times b \times n - p_b \times n > 0$

or, by re-arranging terms:

${p_a \over p_b} > {{1 + b}\over{1 - t - b}}$

This last expression gives us a simple test to determine whether an asset is currently profitable for market making \(the terms on the right are all constant\).

If an asset is profitable for market making, then we'd also like to determine the expected return for this strategy.  From the last chapter, we know that return is ${{gross}\over{cost}} - 1$.  Given the same definitions above, the expected return is therefore:

${{p_a}\over{p_a \times s_t + b \times (p_a + p_b) + p_b}} - 1$

Beyond profitability, this last expression allows us to filter for market making opportunities which exceed a certain return.

We've claimed that market making is a very popular strategy in EVE.  Can you quantify how much market making occurs in the market in a given day?  We explore this topic in our first example for this chapter.

### Example 13 - How much market making is there?

In this example, we'll consider two questions:

1. How many assets are subject to market making? and,
2. How many players are trying to make a market in a given asset?

Orders in EVE's markets are anonymized, so answers to these questions will be estimates at best.  However, we *can* exploit known behavior to refine our answers.  Specifically:

* Assets subject to active market making will have frequently changing best bids and asks as market participants compete to capture order flow; and,
* EVE always shows distinct orders, even if orders have the same price.  This means we can at least put an upper bound on the number of market participants \(a single participant can have multiple orders for an asset, so this can't be an exact bound\).  If these same orders are frequently modified, as one would expect with active market making, then we can estimate an upper bound on the number of active market making participants.



* Definition and technical introduction
** how market makers profit
** mathematics of profitable market making
*** spread must overcome bid/ask broker fee and sales tax
** Example 13 - how much market making is there?

## Elements of a Market Making Strategy
* Elements of a market making strategy
** which assets to trade?
*** liquid assets
*** spreads must be profitable
*** trade volume reasonable balanced between bid and ask
** what does the competition look like?
** how often do I need to change my orders?
* Example 14 - finding market making targets
* Example 15 - simple trade simulator
* Example 16 - computing order change velocity
** managing risk (maintaining stock)
* Example 17 - simple risk projection

## Strategy Effectiveness
* strategy effectiveness
** pros:
*** One of the easiest and cheapest first strategies
** cons:
*** Highly competitive, many 0.01 ISK games
*** Ties up cash in orders (except - margin trading skill)

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
