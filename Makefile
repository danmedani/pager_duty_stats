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

.PHONY: fetch_all
fetch_all:
	@python3 -m pager_duty_stats.print_weekly_stats 0

.PHONY: fetch_some
fetch_some:
	@python3 -m pager_duty_stats.print_weekly_stats 1500 10

.PHONY: break_down
break_down:
	@python3 -m pager_duty_stats.print_type_breakdown 2500


.PHONY: mypy
mypy:
	. virtual_env/bin/activate ;\
	mypy pager_duty_stats

.PHONY: test
test: build mypy
	pytest tests
