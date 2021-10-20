# Builds everything. To be used after first cloning the repo.
.PHONY: init
init: build
	npm install webpack-cli
	make webpack

# Run first:
# python3 -m venv env
# source env/bin/activate
# pip install -r requirements.txt
dev:
	python main.py

# Cleans up, re-installs packages from requirements.txt
env/bin/activate: requirements.txt
	rm -rf virtual_env/
	python3 -m venv virtual_env
	. env/bin/activate ;\
	pip install --upgrade pip ;\
	pip install -rrequirements.txt
	touch env/bin/activate

# Bundle up the javascript code, dev mode (runs in background)
.PHONY: webpackdev
webpackdev:
	npx webpack --mode development --config ui/webpack.config.dev.js


# Build and run the full python test suite. Used as a target in travis CI.
.PHONY: test
test: build lint mypy
	coverage run --source pager_duty_stats -m pytest tests
	coverage report -m --fail-under=80


# Run the full python test suite without first building.
.PHONY: tst
tst:
	coverage run --source pager_duty_stats -m pytest tests
	coverage report -m --fail-under=80


# Bundle up the javascript code, production mode
.PHONY: webpack
webpack:
	npx webpack --mode production --config ui/webpack.config.js


# Delete temporary files & packages
.PHONY: clean
clean:
	rm -fr env
	rm -fr .mypy_cache
	rm -fr .pytest_cache


# Run static type checker for python code.
.PHONY: mypy
mypy:
	@. virtual_env/bin/activate ;\
	mypy pager_duty_stats


# Run linter
.PHONY: lint
lint: 
	@echo "    ----    Re-ordering imports    ----    "
	@find pager_duty_stats tests -name *.py -exec reorder-python-imports {} +
	@echo "    ----    Running linter    ----    "
	@flake8 --config .flake8 pager_duty_stats/ tests/


# You must be Dan to run this
deploy:
	gcloud app deploy