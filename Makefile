.PHONY: clean
clean:
	rm -fr virtual_env

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
	@python3 -m pager_duty_stats.print_weekly_stats 2000
