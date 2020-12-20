default: all

all: style test

style:
	pycodestyle .
.PHONY: style

test: unit_test integration_test
.PHONY: test

# Certain test suites can run automatically embedded with code coverage
# calculation - it is better to run these if time is critical as to not run
# the tests twice.
test-with-coverage: unit_test.cover integration_test.cover
.PHONY: test-with-coverage

UNIT_TEST_CMD=pytest src test/unit_tests
unit_test:
	python3 -m ${UNIT_TEST_CMD}
.PHONY: unit_test

INTEGRATION_TEST_CMD=pytest src test/integration_tests
integration_test:
	python3 -m ${INTEGRATION_TEST_CMD}

coverage_new_dir:
	rm -rf .coverage.COMBINE .coverage.TITLE-tmp
	mkdir .coverage.COMBINE
.PHONY: coverage_new_dir

coverage: coverage_new_dir
	# Clear previously merged coverage data.
	python3 -m coverage erase
	# Execute the coverage targets.
	@$(MAKE) .coverage
	# And create the report
	@$(MAKE) coverage_report
.PHONY: coverage

.coverage: coverage_new_dir unit_test.cover integration_test.cover
	# `coverage combine` deletes the original input files...
	cp *.cover .coverage.COMBINE/
	echo *.cover | sed "s/\.cover//g" >> .coverage.TITLE-tmp
	python3 -m coverage combine .coverage.COMBINE/*

.coverage.TITLE:
	echo -n "Envprobe Coverage (" > .coverage.TITLE
	cat .coverage.TITLE-tmp >> .coverage.TITLE
	echo -n ")" >> .coverage.TITLE
.PHONY: .coverage.TITLE

coverage_report: .coverage.TITLE
	rm -rf htmlcov
	if [ ! -f ".coverage" ]; \
	then \
		echo "No .coverage found, building all..."; \
		$(MAKE) .coverage; \
	fi
	\
	python3 -m coverage report \
		--precision=1 \
		--skip-covered \
		--skip-empty \
		--show-missing
	python3 -m coverage html \
		--precision=1 \
		--skip-covered \
		--skip-empty \
		--title="$(shell cat .coverage.TITLE)"
.PHONY: coverage-report

unit_test.cover:
	python3 -m coverage run -m ${UNIT_TEST_CMD}
	mv .coverage unit_test.cover

unit_test-coverage: coverage_new_dir unit_test.cover
	cp unit_test.cover .coverage.COMBINE/
	python3 -m coverage combine .coverage.COMBINE/*
	echo "unit-tests" >> .coverage.TITLE-tmp
	@$(MAKE) coverage_report
.PHONY: unit_test_coverage

integration_test.cover:
	python3 -m coverage run -m ${INTEGRATION_TEST_CMD}
	mv .coverage integration_test.cover

integration_test-coverage: coverage_new_dir integration_test.cover
	cp integration_test.cover .coverage.COMBINE/
	python3 -m coverage combine .coverage.COMBINE/*
	echo "integration-tests" >> .coverage.TITLE-tmp
	@$(MAKE) coverage_report
.PHONY: integration_test_coverage
