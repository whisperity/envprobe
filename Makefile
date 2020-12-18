default: all

all: style test

style:
	pycodestyle .

.PHONY: style

#PYTHONPATH="${PYTHONPATH}:$(shell git rev-parse --show-toplevel)/src"
test:
	python3 -m pytest \
		--capture=no \
		--verbose

.PHONY: test
