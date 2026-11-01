PYTHON ?= python3

.PHONY: build check eval
build:
	$(PYTHON) scripts/check_package.py --build

check:
	$(PYTHON) scripts/check_package.py
	$(PYTHON) -m unittest discover -s tests -v

eval:
	$(PYTHON) scripts/evaluate_dev.py
