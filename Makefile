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
	touch virtual_env/bin/activate  # update so it's as new as requirements-minimal.txt

.PHONY: fetch_all
fetch_all:
	@python aggregate.py 0

.PHONY: fetch_recent
fetch_recent:
	@python aggregate.py 3000
