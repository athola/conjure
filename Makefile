.PHONY: help deps check fix format lint typecheck spellcheck security-check test status clean install-hooks validate-all quota-status usage-report validate-delegation delegate-status delegate-verify delegate-usage delegate-test delegate-gemini delegate-qwen delegate-auto

# Default target
help:
	@echo "Available commands:"
	@echo "  deps        - Install and sync dependencies"
	@echo "  check       - Run dependency validation"
	@echo "  fix         - Auto-fix code style issues"
	@echo "  format      - Format Python code"
	@echo "  lint        - Run linting checks"
	@echo "  test        - Run all quality checks"
	@echo "  precommit   - Run pre-commit against all files"
	@echo "  status      - Show project overview"
	@echo "  clean       - Clean cache and build files"
	@echo "  install-hooks - Install pre-commit hooks"
	@echo ""
	@echo "Delegation commands:"
	@echo "  quota-status    - Check delegation quota status"
	@echo "  usage-report    - Generate usage report"
	@echo "  validate-delegation - Validate delegation configuration"
	@echo "  delegate-status - Check delegation service availability"
	@echo "  delegate-verify - Verify authentication for all services"
	@echo "  delegate-usage  - Show usage analytics across services"
	@echo "  delegate-test   - Test all delegation services"
	@echo ""
	@echo "Usage examples:"
	@echo "  make delegate-gemini PROMPT='Analyze code' FILES='src/main.py'"
	@echo "  make delegate-qwen PROMPT='Extract patterns' FILES='src/**/*.py'"
	@echo "  make delegate-auto PROMPT='Best analysis' FILES='src/'"

# Dependency management
deps:
	uv sync

check:
	@echo "Running dependency validation..."
	uv run python tools/quota_tracker.py --status || true
	uv run python tools/usage_logger.py --validate || true

fix:
	@echo "Auto-fixing code style issues..."
	uv run ruff format tools/ hooks/
	uv run ruff check --fix tools/ hooks/

# Code quality
format:
	@echo "Formatting Python code..."
	uv run ruff format tools/ hooks/
	uv run ruff check --fix tools/ hooks/

lint:
	@echo "Running linting checks..."
	uv run ruff check tools/ hooks/

typecheck:
	@echo "Running type checking..."
	uv run mypy tools/
	uv run ty check tools/

spellcheck:
	@echo "Running spell check..."
	uv run typos tools/ hooks/

security-check:
	@echo "Running security checks..."
	uv run bandit -r tools/ hooks/

test: check lint typecheck security-check
	@echo "All checks passed!"

precommit:
	@echo "Running pre-commit hooks..."
	uv run pre-commit run --all-files

# Git and hooks
install-hooks:
	@echo "Installing pre-commit hooks..."
	uv run pre-commit install

validate-all:
	@echo "Running full validation..."
	uv run python tools/quota_tracker.py --status
	uv run python tools/usage_logger.py --validate
	uv run pre-commit run --all-files || true

# Maintenance
clean:
	@echo "Cleaning up..."
	rm -rf .venv
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	uv cache clean

# Quick commands
status:
	@echo "Current status:"
	@echo "Skills: $$(find skills/ -name 'SKILL.md' | wc -l) skill files"
	@echo "Tools: $$(find tools/ -name '*.py' | wc -l) Python files"
	@echo "Hooks: $$(find hooks/ -name '*.py' | wc -l) hook files"

# Delegation specific commands
quota-status:
	@echo "Checking delegation quota status..."
	uv run python tools/quota_tracker.py --status

usage-report:
	@echo "Generating usage report..."
	uv run python tools/usage_logger.py --report

validate-delegation:
	@echo "Validating delegation configuration..."
	uv run python tools/quota_tracker.py --validate-config

# Delegation executor commands
delegate-status:
	@echo "Checking delegation service status..."
	uv run python tools/delegation_executor.py --list-services

delegate-verify:
	@echo "Verifying delegation services..."
	uv run python tools/delegation_executor.py gemini --verify || true
	uv run python tools/delegation_executor.py qwen --verify || true

delegate-usage:
	@echo "Showing delegation usage analytics..."
	uv run python tools/delegation_executor.py --usage

delegate-gemini:
	@echo "Delegating to Gemini..."
	uv run python tools/delegation_executor.py gemini "$(PROMPT)" $(if $(FILES),--files $(FILES))

delegate-qwen:
	@echo "Delegating to Qwen..."
	uv run python tools/delegation_executor.py qwen "$(PROMPT)" $(if $(FILES),--files $(FILES))

delegate-auto:
	@echo "Auto-selecting best delegation service..."
	uv run python tools/delegation_executor.py auto "$(PROMPT)" $(if $(FILES),--files $(FILES))

delegate-test:
	@echo "Testing delegation services..."
	@echo "Testing Gemini..."
	uv run python tools/delegation_executor.py gemini "Respond with 'OK'" || echo "Gemini not available"
	@echo "Testing Qwen..."
	uv run python tools/delegation_executor.py qwen "Respond with 'OK'" || echo "Qwen not available"
	@echo "Showing usage..."
	uv run python tools/delegation_executor.py --usage
