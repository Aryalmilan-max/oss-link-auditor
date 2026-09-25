.PHONY: setup test demo check

setup:
	python3 -m venv .venv
	.venv/bin/python -m pip install -e ".[dev]"

test:
	PYTHONPATH=src python3 -m unittest discover -s tests -v

demo:
	PYTHONPATH=src python3 scripts/demo.py

check: test demo
	.venv/bin/ruff format --check .
	.venv/bin/ruff check .
	.venv/bin/mypy src
	PYTHONPATH=src python3 -m compileall -q src tests scripts
