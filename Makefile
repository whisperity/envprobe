default: all

all: style test

style:
	pycodestyle .

.PHONY: style

test:
	#PYTHONPATH="${PYTHONPATH}:$(shell git rev-parse --show-toplevel)/src"
	python3 -m pytest \
		--capture=no \
		--verbose

.PHONY: test
