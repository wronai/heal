.PHONY: help install install-dev test lint format clean build publish

# Default target
help:
	@echo "Available commands:"
	@echo "  install      Install package"
	@echo "  install-dev  Install package in development mode"
	@echo "  test         Run tests"
	@echo "  lint         Run linting"
	@echo "  format       Format code"
	@echo "  clean        Clean build artifacts"
	@echo "  build        Build package"
	@echo "  publish      Publish to PyPI"

# Install package
install:
	pip install .

# Install in development mode
install-dev:
	pip install -e .[dev]

# Run tests
test:
	python -m pytest -v

# Run tests with coverage
test-cov:
	python -m pytest --cov=heal --cov-report=html --cov-report=term

# Lint code
lint:
	python -m flake8 heal/
	python -m mypy heal/

# Format code
format:
	python -m black heal/
	python -m isort heal/

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Build package
build: clean
	python -m build

# Publish to PyPI
publish: build
	python -m twine upload dist/*

# Publish to test PyPI
publish-test: build
	python -m twine upload --repository testpypi dist/*

# Development setup
dev:
	pip install -e .[dev]
	pre-commit install

# Run CLI
cli:
	heal --help
