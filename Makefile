include_dir=build
source=chapters/*.md
title='EVE Market Strategies'
filename=eve-market-strategies

all: html epub rtf pdf mobi

clean:
	rm -f index.html
	rm -f $(filename).epub
	rm -f $(filename).md
	rm -f $(filename).mobi
	rm -f $(filename).pdf
	rm -f $(filename).rtf

markdown:
	awk 'FNR==1{print ""}{print}' $(source) > $(filename).md

html: markdown
	pandoc -s $(filename).md -t html5 -o index.html -c style.css \
		--include-in-header $(include_dir)/head.html \
		--include-before-body $(include_dir)/author.html \
		--include-before-body $(include_dir)/share.html \
		--include-after-body $(include_dir)/stats.html \
		--webtex \
		--title-prefix $(title) \
		--normalize \
		--smart \
		--toc

epub: markdown
	pandoc -s $(filename).md --normalize --smart -t epub -o $(filename).epub \
		--epub-metadata $(include_dir)/metadata.xml \
		--epub-stylesheet epub.css \
		--epub-cover-image img/logo__lettering_background_256_256.png \
		--title-prefix $(title) \
		--normalize \
		--smart \
		--toc

rtf: markdown
	pandoc -s $(filename).md -o $(filename).rtf \
		--title-prefix $(title) \
		--normalize \
		--smart

pdf: markdown
	pandoc -s $(filename).md -o $(filename).pdf \
		--variable=papersize:"letter" \
		--title-prefix=$(title) \
		--normalize \
		--smart \
		--toc \
		--latex-engine=pdflatex

mobi: epub
	# Download: http://www.amazon.com/gp/feature.html?ie=UTF8&docId=1000765211
	kindlegen $(filename).epub
