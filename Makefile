
generate-docs:
	mkdocs new .

serve-docs:
	mkdocs serve -a localhost:8010

build-docs:
	mkdocs build

local-install:
	pip install -e .

test:
	coverage run --rcfile ./pyproject.toml -m pytest ./tests
	coverage report --fail-under 95