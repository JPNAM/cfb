PYTHON ?= python
NODE ?= npm
SEASONS ?= 2023 2024

.PHONY: up etl test

up:
	docker compose up --build

etl:
	PYTHONPATH=backend $(PYTHON) backend/etl/etl_load_nflverse.py --seasons $(SEASONS)
	PYTHONPATH=backend $(PYTHON) backend/etl/etl_load_coaches.py
	PYTHONPATH=backend $(PYTHON) backend/etl/etl_compute_states.py
	PYTHONPATH=backend $(PYTHON) backend/etl/etl_aggregates.py

test:
	PYTHONPATH=backend pytest

