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
