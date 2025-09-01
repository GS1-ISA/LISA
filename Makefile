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

.PHONY: bench-q11 bench-q12
bench-q11:
	python3 scripts/bench_q11_orjson.py | tee docs/research/q11_orjson_determinism/results.md

bench-q12:
	python3 scripts/bench_q12_validation.py | tee docs/research/q12_compiled_validators/results.md
