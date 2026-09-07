.PHONY: setup lab1 lab2 lab3 lab4 test test-solutions compare scoreboard lint verify clean

PYTHON ?= python

# macOS + Homebrew's libomp can double-initialize under faiss+torch; harmless
# on Linux/Codespaces, so this is set unconditionally rather than guarded.
export KMP_DUPLICATE_LIB_OK=TRUE

setup:
	pip install -e ".[dev]"

## Run each lab's __main__ against a sample query, so you can see it work
## without writing a test first.
lab1:
	$(PYTHON) -m labs.lab01_simple_rag

lab2:
	$(PYTHON) -m labs.lab02_query_optimization

lab3:
	$(PYTHON) -m labs.lab03_hybrid_rrf

lab4:
	$(PYTHON) -m labs.lab04_reranking

## Run the fixed test suite against your labs/ implementation (default) or
## the reference solutions: `make test RAG_IMPL=solutions`.
test:
	RAG_IMPL=$${RAG_IMPL:-labs} $(PYTHON) -m pytest -v

test-solutions:
	RAG_IMPL=solutions $(PYTHON) -m pytest -v

## Run one query through all four pipelines side by side:
##   make compare Q="What causes error E-4021?"
compare:
	$(PYTHON) -m ragkit.compare "$(Q)"

## Evaluate all four pipelines against the gold query set and print the
## comparison table. Pass RAG_IMPL=solutions to score the reference instead.
scoreboard:
	RAG_IMPL=$${RAG_IMPL:-labs} $(PYTHON) -m ragkit.scoreboard --run

lint:
	ruff check .

## Full sanity pass: lint, run tests against the reference solutions (this
## is what proves every fixed test is satisfiable), and render a scoreboard.
verify: lint
	RAG_IMPL=solutions RAG_LLM=offline $(PYTHON) -m pytest -q
	RAG_IMPL=solutions RAG_LLM=offline $(PYTHON) -m ragkit.scoreboard --run

clean:
	rm -rf data/.cache .pytest_cache .ruff_cache
	find . -name "__pycache__" -type d -exec rm -rf {} +
