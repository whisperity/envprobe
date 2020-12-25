default: all

all: style test static_analysis docs

style:
	flake8 src/ test/
.PHONY: style

static_analysis: bandit

bandit:
	bandit -r src/envprobe
	bandit -s B101,B311 -r test
.PHONY: bandit

test: unit_test integration_test system_test
.PHONY: test

# Certain test suites can run automatically embedded with code coverage
# calculation - it is better to run these if time is critical as to not run
# the tests twice.
test-with-coverage: unit_test.cover integration_test.cover
.PHONY: test-with-coverage

UNIT_TEST_CMD=pytest src test/unit
unit_test:
	python3 -m ${UNIT_TEST_CMD}
.PHONY: unit_test

INTEGRATION_TEST_CMD=pytest src test/integration
integration_test:
	python3 -m ${INTEGRATION_TEST_CMD}

SYSTEM_TEST_CMD=pytest src test/system
system_test:
	python3 -m ${SYSTEM_TEST_CMD}

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

.coverage: coverage_new_dir unit_test.cover integration_test.cover system_test.cover
	# `coverage combine` deletes the original input files...
	cp *.cover .coverage.COMBINE/
	echo *.cover | sed "s/\_test.cover//g" >> .coverage.TITLE-tmp
	python3 -m coverage combine .coverage.COMBINE/*

.coverage.TITLE:
	echo -n "Envprobe Coverage (" > .coverage.TITLE
	cat .coverage.TITLE-tmp | tr -d '\n' >> .coverage.TITLE
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
	echo "unit" >> .coverage.TITLE-tmp
	@$(MAKE) coverage_report
.PHONY: unit_test-coverage

integration_test.cover:
	python3 -m coverage run -m ${INTEGRATION_TEST_CMD}
	mv .coverage integration_test.cover

integration_test-coverage: coverage_new_dir integration_test.cover
	cp integration_test.cover .coverage.COMBINE/
	python3 -m coverage combine .coverage.COMBINE/*
	echo "integration" >> .coverage.TITLE-tmp
	@$(MAKE) coverage_report
.PHONY: integration_test-coverage

system_test.cover:
	# TODO: System tests don't seem to generate useful coverage...
	python3 -m coverage run -m ${SYSTEM_TEST_CMD}
	mv .coverage system_test.cover

system_test-coverage: coverage_new_dir system_test.cover
	cp system_test.cover .coverage.COMBINE/
	python3 -m coverage combine .coverage.COMBINE/*
	echo "functional" >> .coverage.TITLE-tmp
	@$(MAKE) coverage_report
.PHONY: system_test-coverage

docs: docs-html

docs-html:
	$(MAKE) -C docs/ html
.PHONY: docs-html

clean:
	rm -rf *.cover .coverage* htmlcov
	rm -rf docs/_build
.PHONY: clean
