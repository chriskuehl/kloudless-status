SHELL = /bin/sh
JS_COMPRESSOR = ./node_modules/uglify-js/bin/uglifyjs

JS_SOURCES = js/balanced.lib.src.js \
             js/status.src.js \
             js/subscribe.src.js
all: node_modules \
    js/status.min.js

js/status.min.js: $(JS_SOURCES)
	cat $^ | $(JS_COMPRESSOR) > $@

clean:
	rm -rf js/status.min.js

node_modules: package.json
	npm install
	touch node_modules
