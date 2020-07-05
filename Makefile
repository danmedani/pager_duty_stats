.PHONY: clean
clean:
	rm -fr virtual_env
	rm -fr .mypy_cache
	rm -fr .pytest_cache

.PHONY: build
build: clean venv/bin/activate

venv/bin/activate: requirements-minimal.txt
	rm -rf virtual_env/
	python3 -m venv virtual_env
	. virtual_env/bin/activate ;\
	pip install --upgrade pip ;\
	pip install -Ur requirements-minimal.txt ;\
	pip freeze | sort > requirements.txt
	touch virtual_env/bin/activate

.PHONY: mypy
mypy:
	@. virtual_env/bin/activate ;\
	mypy pager_duty_stats

.PHONY: test
test: build lint mypy
	coverage run --source pager_duty_stats -m pytest tests
	coverage report -m --fail-under=100

# Not building beforehand makes testing in dev faster
.PHONY: tst
tst: lint mypy
	coverage run --source pager_duty_stats -m pytest tests
	coverage report -m --fail-under=100

.PHONY: lint
lint: 
	@echo "    ----    Re-ordering imports    ----    "
	@find pager_duty_stats tests -name *.py -exec reorder-python-imports {} +
	@echo "    ----    Running linter    ----    "
	@flake8 --config .flake8 pager_duty_stats/ tests/
	coverage report -m

.PHONY: webpack
webpack:
	npx webpack --mode production --config ui/webpack.config.js

.PHONY: web
web: webpack
	uwsgi --http 127.0.0.1:3031 --wsgi-file pager_duty_stats/webserver.py --callable app --processes 4 --threads 2 --stats 127.0.0.1:9191
