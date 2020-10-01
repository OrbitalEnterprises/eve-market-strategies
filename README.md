# EVE Market Strategies <a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png" /></a> <a rel="license" href="https://opensource.org/licenses/MIT"><img alt="MIT License" style="border-width:0" src="https://raw.githubusercontent.com/legacy-icons/license-icons/master/dist/32x32/mit.png" /></a>

This is an open-source book which describes the development of market trading strategies in [EVE Online](https://www.eveonline.com/), a massively-multiplayer online game.  We're releasing this book under the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License](http://creativecommons.org/licenses/by-nc-sa/4.0/), which roughly means you can mangle it all you want and share the result as long as you attribute the original work and you don't charge anything.  A copy of this license is included in the [LICENSE-BOOK](LICENSE-BOOK) file.  The source code available in this repository is released under the [MIT License](https://opensource.org/licenses/MIT) a copy of which is included in the [LICENSE-CODE](LICENSE-CODE) file.  We're not planning to ever charge a fee for this work, but if you'd like to show your appreciation you can donate in game to "Salacious Necrosis".

The structure of this repository was copied from the [Backbone Fundamentals](https://github.com/addyosmani/backbone-fundamentals) open source book.  

## Who Should Read This Book?

This book attempts to be a systematic discussion of data driven analysis and trading strategies in EVE's markets.  That said, the text is intended to be enjoyed by a broad audience.  If market analysis, data science, or coding aren't your things, we hope you'll at least gain a better understanding of some of the forces \(and the players behind them\) which drive EVE's markets.  Conversely, market professionals will hopefully learn a few new tricks and find our code examples a useful starting point for their own strategies.  EVE's markets are complex.  We've certainly made errors in this work, and we don't claim to have a complete understanding of every factor which drives the markets.  If you find places where we've made mistakes, or you'd like to offer your own insight, please consider contributing as described below.

## Downloads

The latest fully assembled Markdown version of the book will always be available in the repository [here](eve-market-strategies.md).  You can also view the latest version in web page format [here](https://orbitalenterprises.github.io/eve-market-strategies/index.html).  Other versions of the book will be available in our public Google Drive folder [here](https://drive.google.com/open?id=0B6lvkwGmS7a2NWkyc21zbHVmbEE).  Cloning and building the repository is always the best way to get the most recent version of the book.

## Contributing

This is less of a book and more of a live document.  We appreciate and welcome all efforts to improve the book.  We've organized the repo as follows:

* *build* - contains various templates used to compile the book.
* *chapters* - contains the Markdown source for each book section.
* *code* - contains code samples and Jupyter notebooks referenced in the text.
* *img* - contains images referenced in the text.

We welcome all pull requests.  Changes to the book text should be pull requests against the relevant Markdown in *chapters*.  If you'd like to contribute whole sections or chapters, we're open to that too.  Raise an appropriately titled issue if you have suggestions or something large you'd like to contribute.

## Building

We've set up a simple make file to build the book which should work on most variants of UNIX \(we've tested with Cygwin for Windows and have verified that it works there as well\).  You'll need at least the following software packages to use the make file:

* An OS appropriate version of [Make](https://www.gnu.org/software/make/).
* An OS appropriate version of [Pandoc](https://github.com/jgm/pandoc).
* An OS appropriate version of [TeX](https://en.wikipedia.org/wiki/TeX) which includes pdflatex \(included in most modern distributions\).

Use the command `make` or `make -f Makefile` to build the book.  The build will output versions of the book in Markdown, HTML, ePub, Mobi \(Kindle\), PDF and RTF.  

## Legal Information

EVE Online is Copyright (c) CCP Games 1997-2017.  Use of the third party APIs provided by CCP, and the data exposed by these APIs, is subject to the [DEVELOPER LICENSE AGREEMENT](https://developers.eveonline.com/resource/license-agreement).
