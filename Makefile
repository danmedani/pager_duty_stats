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
	. virtual_env/bin/activate ;\
	mypy pager_duty_stats

.PHONY: test
test: build mypy
	coverage run --source pager_duty_stats -m pytest tests
	coverage report -m

# Not building beforehand makes things faster
.PHONY: tst
tst: mypy
	coverage run --source pager_duty_stats -m pytest tests
	coverage report -m
