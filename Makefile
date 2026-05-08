.PHONY: demo dashboard evaluate heartbeat casepack risk-register import-demo test lint format check clean help

PYTHONPATH := src

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'

demo: ## Run fixture triage and generate all demo artifacts
	PYTHONPATH=$(PYTHONPATH) python scripts/run_demo.py

dashboard: ## Launch Streamlit dashboard on :8501
	PYTHONPATH=$(PYTHONPATH) python -m streamlit run dashboard/app.py --server.port 8501 --server.headless true

evaluate: ## Generate evaluation report
	PYTHONPATH=$(PYTHONPATH) python scripts/generate_evaluation_report.py

heartbeat: ## Generate eval health heartbeat
	PYTHONPATH=$(PYTHONPATH) python scripts/generate_heartbeat.py

casepack: ## Generate demo cluster casepack
	PYTHONPATH=$(PYTHONPATH) python scripts/generate_casepack.py

risk-register: ## Generate emerging AI risk register
	PYTHONPATH=$(PYTHONPATH) python scripts/generate_risk_register.py

error-analysis: ## Generate error analysis report
	PYTHONPATH=$(PYTHONPATH) python scripts/generate_error_analysis.py

import-demo: ## Normalize the fixture data through the generic import adapter
	PYTHONPATH=$(PYTHONPATH) python scripts/import_cases.py --input fixtures/eval_cases.json --output out/imported_eval_cases.json --format json

test: ## Run pytest suite
	PYTHONPATH=$(PYTHONPATH) python -m pytest tests/ -v

lint: ## Check formatting, imports, and lint rules
	PYTHONPATH=$(PYTHONPATH) python -m ruff check .
	PYTHONPATH=$(PYTHONPATH) python -m black --check .

format: ## Format Python code and organize imports
	PYTHONPATH=$(PYTHONPATH) python -m isort .
	PYTHONPATH=$(PYTHONPATH) python -m black .
	PYTHONPATH=$(PYTHONPATH) python -m ruff check . --fix

check: lint test ## Run lint and tests

clean: ## Remove generated runtime artifacts
	rm -f out/triage_run.json out/imported_eval_cases.json
	rm -f docs/evaluation_report.md docs/eval_health_heartbeat.md docs/demo_casepack.md docs/emerging_ai_risk_register.md docs/error_analysis.md
	@echo "Cleaned generated demo artifacts."
