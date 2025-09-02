.PHONY: setup lint fix typecheck test ci

setup:
	python -m pip install --upgrade pip
	pip install ruff mypy pytest pytest-cov bandit pip-audit radon

lint:
	ruff format --check .
	ruff check .

fix:
	ruff format .
	ruff check --fix .

typecheck:
	mypy ISA_SuperApp/src

test:
	pytest -q

ci: lint typecheck test

.PHONY: api
api:
	cd ISA_SuperApp && python -m uvicorn src.api_server:app --host 127.0.0.1 --port 8787 --reload

.PHONY: clean
clean:
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +
	find . -name '*.py[co]' -delete
	rm -rf .pytest_cache .mypy_cache .mypy_linecount .coverage coverage.xml
	rm -f semgrep.json
	rm -f ISA_SuperApp/coverage.xml
	rm -rf agent/outcomes || true
	rm -rf .lineage || true
	find . -name '.DS_Store' -delete

.PHONY: index
index:
	python3 scripts/index_repo.py || python scripts/index_repo.py

.PHONY: outcomes-summary docs-lint pr-notes
outcomes-summary:
	python3 scripts/outcomes_summary.py || python scripts/outcomes_summary.py

docs-lint:
	python3 scripts/docs_ref_lint.py || python scripts/docs_ref_lint.py

pr-notes:
	python3 scripts/prepare_pr_notes.py || python scripts/prepare_pr_notes.py

.PHONY: bench-q11 bench-q12
bench-q11:
	python3 scripts/bench_q11_orjson.py | tee docs/research/q11_orjson_determinism/results.md

bench-q12:
	python3 scripts/bench_q12_validation.py | tee docs/research/q12_compiled_validators/results.md

.PHONY: api otel-up otel-down
api:
	cd ISA_SuperApp && python -m uvicorn src.api_server:app --host 127.0.0.1 --port 8787 --reload

otel-up:
	docker compose -f infra/otel/docker-compose.yml up -d

otel-down:
	docker compose -f infra/otel/docker-compose.yml down

.PHONY: prom-up prom-down
prom-up:
	docker compose -f infra/monitoring/docker-compose.yml up -d

prom-down:
	docker compose -f infra/monitoring/docker-compose.yml down

.PHONY: healthcheck
healthcheck:
	python3 scripts/healthcheck.py


.PHONY: size-budget
size-budget:
	python3 scripts/size_budget.py || python scripts/size_budget.py
