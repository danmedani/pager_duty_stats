# Builds everything. To be used after first cloning the repo.
.PHONY: init
init: build
	npm install webpack-cli
	make webpack


# Run webserver in dev environment
.PHONY: web
web:
	uwsgi --http 127.0.0.1:3031 --wsgi-file pager_duty_stats/application.py --callable application --processes 4 --threads 2 --stats 127.0.0.1:9191


# Bundle up the javascript code, dev mode (runs in background)
.PHONY: webpackdev
webpackdev:
	npx webpack --mode development --config ui/webpack.config.dev.js


# Build backend
.PHONY: build
build: clean venv/bin/activate


# Build and run the full python test suite. Used as a target in travis CI.
.PHONY: test
test: build lint mypy
	coverage run --source pager_duty_stats -m pytest tests
	coverage report -m --fail-under=70


# Run the full python test suite without first building.
.PHONY: tst
tst: lint mypy
	coverage run --source pager_duty_stats -m pytest tests
	coverage report -m --fail-under=70


# Bundle up the javascript code, production mode
.PHONY: webpack
webpack:
	npx webpack --mode production --config ui/webpack.config.js


# Delete temporary files & packages
.PHONY: clean
clean:
	rm -fr virtual_env
	rm -fr .mypy_cache
	rm -fr .pytest_cache


# Clears out and installs packages and dependencies using requirements-minimal.txt
venv/bin/activate: requirements-minimal.txt
	rm -rf virtual_env/
	python3 -m venv virtual_env
	. virtual_env/bin/activate ;\
	pip install --upgrade pip ;\
	pip install -Ur requirements-minimal.txt ;\
	pip freeze | sort > requirements.txt
	touch virtual_env/bin/activate


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


# Package the code up and deploy to aws
.PHONY: package
package: build webpack
	eb deploy PagerDutyStats-env
	eb open PagerDutyStats-env
