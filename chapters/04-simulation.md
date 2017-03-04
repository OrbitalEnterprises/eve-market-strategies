# Simulating Trading Strategies \(Planned\)

* Types of testing
  * Backtesting
    * In vs. out of sample data, overfit, etc.
  * Paper trading
* Decide what you're going to measure
  * Total profit, Return, Volatility \(Risk\), etc.

## Using Zipline to Backtest EVE Trading Strategies

* Quick intro to Zipline
  * Making an EVE market look like a Zipline market
* EVE data bundle
  * Region market summaries
  * Each region is an "exchange"
* Other EVE data
  * Region book data
    * Download as part of EVE data bundle
    * Accessible through EVE library
  * Region price data
    * Download as part of EVE data bundle
    * Accessible through EVE libray
  * SDE data
    * Doesn't work if you go too far back, unless you have other sources 
      because sometimes things in the SDE change with each release
  * Order matching library
    * Limited data for citadels

### Example - Evaluating the Cross Region Trading Strategy in Zipline

* Implement liquidity filter
* Implement region trade finder
* Submit "buy" orders
* Simulate transportation delay after buy orders
  * Simulating buy orders at other stations
* Submit "sell" orders
* Show expected profit
