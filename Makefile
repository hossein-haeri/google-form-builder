.PHONY: help install install-dev test clean lint format example demo

help:  ## Show this help message
	@echo "Google Form Builder - Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install the package and dependencies
	pip install -r requirements.txt
	pip install -e .

install-dev:  ## Install with development dependencies
	pip install -r requirements.txt
	pip install -e ".[dev]"

test:  ## Run tests (when implemented)
	@echo "Tests not yet implemented"
	# pytest tests/

clean:  ## Clean up temporary files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .coverage htmlcov/ .pytest_cache/

lint:  ## Run linting (when dev dependencies installed)
	@echo "Linting tools not configured yet"
	# flake8 google_form_builder/ cli.py
	# mypy google_form_builder/

format:  ## Format code (when dev dependencies installed)
	@echo "Code formatting not configured yet"
	# black google_form_builder/ cli.py

example:  ## Generate example files
	python cli.py example examples/demo_questions.json
	python cli.py example examples/demo_questions.csv --format csv
	@echo "Example files created in examples/ directory"

demo:  ## Run a demo (validate example files)
	@echo "🔍 Validating JSON example..."
	python cli.py create examples/sample_questions.json --validate-only
	@echo ""
	@echo "🔍 Validating CSV example..."
	python cli.py create examples/sample_questions.csv --validate-only

check-credentials:  ## Check if credentials are set up
	@if [ -f "credentials.json" ]; then \
		echo "✅ Credentials file found: credentials.json"; \
	else \
		echo "❌ Credentials file not found."; \
		echo "Please create credentials.json or use --credentials flag"; \
		echo "See README.md for setup instructions"; \
	fi

formats:  ## Show supported input formats
	python cli.py formats

types:  ## Show supported question types
	python cli.py types

quick-start:  ## Quick start guide
	@echo "🚀 Google Form Builder Quick Start"
	@echo "=================================="
	@echo ""
	@echo "1. Set up credentials (see README.md)"
	@echo "2. Generate example: make example"
	@echo "3. Validate input: make demo"
	@echo "4. Create form: python cli.py create examples/sample_questions.json --credentials credentials.json"
	@echo ""
	@echo "For more help: make help"

uninstall:  ## Uninstall the package
	pip uninstall google-form-builder -y 