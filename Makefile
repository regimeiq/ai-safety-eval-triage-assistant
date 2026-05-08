.PHONY: demo dashboard evaluate heartbeat casepack risk-register test clean help

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

test: ## Run pytest suite
	PYTHONPATH=$(PYTHONPATH) python -m pytest tests/ -v

clean: ## Remove generated runtime artifacts
	rm -f out/triage_run.json
	rm -f docs/evaluation_report.md docs/eval_health_heartbeat.md docs/demo_casepack.md docs/emerging_ai_risk_register.md
	@echo "Cleaned generated demo artifacts."
