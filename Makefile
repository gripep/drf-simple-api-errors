.PHONY : install shell format lint test test/cov

# Install dependencies with poetry
install:
	@poetry install --with dev -v

# Run formatters (black, isort) with poetry
format:
	@poetry run isort drf_simple_api_errors integration_tests tests
	@poetry run black drf_simple_api_errors integration_tests tests

# Check format (black, isort) and linting (flake8)
lint:
	@poetry run isort --check drf_simple_api_errors integration_tests tests
	@poetry run black --check drf_simple_api_errors integration_tests tests --exclude migrations
	@poetry run flake8 drf_simple_api_errors integration_tests tests --max-line-length 88

# Run unittests with poetry
test:
	@poetry run pytest

# Run code coverage tests coverage with poetry
test/cov:
	@poetry run pytest --cov=drf_simple_api_errors --cov-report xml:coverage.xml
