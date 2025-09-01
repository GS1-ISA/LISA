SHELL := /bin/bash
VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

.PHONY: setup install dev run run-flow lint format mypy test docs clean zip audit sbom

setup: $(VENV)/bin/activate
	@echo "✔ venv ready"

$(VENV)/bin/activate:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev,test]"

install:
	$(PIP) install -e ".[dev,test]"

dev: install pre-commit
	@echo "✔ dev env ready"

pre-commit:
	$(PIP) install pre-commit
	$(VENV)/bin/pre-commit install

run: 
	ISA_OFFLINE?=1 $(PYTHON) -m isa_c

run-flow:
	USE_PREFECT=1 $(PYTHON) -m isa_c --flow

lint:
	$(VENV)/bin/ruff check .
format:
	$(VENV)/bin/black .
mypy:
	$(VENV)/bin/mypy .

test:
	$(PYTHON) -m pytest --cov=isa_c --cov-report=term-missing

docs:
	$(VENV)/bin/mkdocs build

clean:
	rm -rf $(VENV) .mypy_cache .pytest_cache site dist build logs data .cache

zip:
	python - <<'PY'
import zipfile, os
with zipfile.ZipFile('ISA_C_full.zip', 'w', zipfile.ZIP_DEFLATED) as z:
  for root, _, files in os.walk('.', topdown=True):
    if root.startswith('./.venv') or root.startswith('./.git'): 
      continue
    for f in files:
      p = os.path.join(root, f)
      z.write(p, p)
print('Wrote ISA_C_full.zip')
PY

audit:
	@echo "Run safety/pip-audit if installed"

sbom:
	@echo "Run cyclonedx-bom if installed"


autodev-run:
	python -m autodev.main

autodev-loop:
	python -m autodev.main --loop --sleep=15



.PHONY: venv install fmt lint type test precommit ci-all docker-up docker-build

venv:
	python3 -m venv .venv

install: venv
	. .venv/bin/activate && python -m pip install -U pip && pip install -r requirements.txt || true
	. .venv/bin/activate && pip install -r requirements-dev.txt

fmt:
	. .venv/bin/activate && ruff check --fix . && ruff format . && black . && isort .

lint:
	. .venv/bin/activate && ruff check . && black --check .

type:
	. .venv/bin/activate && mypy || true

test:
	. .venv/bin/activate && pytest

precommit:
	. .venv/bin/activate && pre-commit install && pre-commit run -a

ci-all: install fmt lint type test

docker-build:
	docker build -t isa_c:local .

docker-up:
	docker compose up --build
