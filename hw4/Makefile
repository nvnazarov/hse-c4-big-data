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
	@echo "[running formatter]"
	@uv run ruff format dags/ tests/
	@echo "[formatter finished]"

test:
	@echo "[running tests]"
	@uv run pytest
	@echo "[all tests run]"
