generate-ssl-certificates:
	@echo "[generating new ssl certificates]"
	@sh ./scripts/generate_ssl_certificates.sh ./ssl
	@echo "[generated certificates at ./ssl]"

up:
	@echo "[starting docker compose]"
	@echo "AIRFLOW_UID=$(shell id -u)" > .env
	@docker compose up --build -d
	@echo "[started docker compose in background]"

down:
	@echo "[stopping docker compose]"
	@docker compose down
	@echo "[stopped docker compose]"

lint:
	@echo "[running linter]"
	@uv run ruff check dags/ --select AIR3
	@echo "[linter finished]"

format:
	@echo "[running formatters]"
	@uv run ruff format dags/ tests/
	@uv run isort dags/ tests/
	@echo "[formatters finished]"

test:
	@echo "[running tests]"
	@uv run pytest
	@echo "[all tests run]"

show-dirty-products:
	@echo "[loading dirty products]"
	@docker compose exec postgres psql -U airflow -d airflow -c "SELECT COUNT(*) FROM dirty_products"

show-cleaned-products:
	@echo "[loading dirty products]"
	@docker compose exec postgres psql -U airflow -d airflow -c "SELECT COUNT(*) FROM products"
