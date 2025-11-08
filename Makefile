install:
	poetry install
run:
	poetry run database
build:
	poetry build
publish:
	poetry publish --dry-run
lint:
	poetry run ruff check .
package-install:
	python3 -m pip install --force-reinstall dist/*.whl

