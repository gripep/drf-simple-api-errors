.PHONY : help test install

format:  ## Run formatters (black, isort) with poetry
	poetry run isort drf_simple_api_errors test_project
	poetry run black drf_simple_api_errors test_project

install:  ## Install dependencies with poetry
	poetry install --with dev -v

lint:  ## Check format (black, isort) and linting (flake8)
	poetry run isort --check drf_simple_api_errors test_project
	poetry run black --check drf_simple_api_errors test_project --exclude migrations
	poetry run flake8 drf_simple_api_errors test_project --max-line-length 88

shell:  ## Run poetry shell
	poetry shell

test:  ## Run unittests with poetry
	poetry run pytest test_project

test/cov:  ## Run code coverage tests coverage with poetry
	poetry run pytest test_project --cov=drf_simple_api_errors
