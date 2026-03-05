qa:
	@echo "[formatters: start]"
	@uv run ruff format ./dags
	@uv run isort ./dags
	@echo "[formatters: ok]"
	@echo "[linters: start]"
	@uv run ruff check
	@echo "[linters: ok]"

requirements:
	@uv export --no-dev > requirements.txt
