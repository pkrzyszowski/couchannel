.PHONY: compose-up compose-down compose-build compose-logs lint test

compose-up:
	@docker compose up --build

compose-down:
	@docker compose down --remove-orphans

compose-build:
	@docker compose build

compose-logs:
	@docker compose logs -f

lint:
	ruff check services tests

test:
	./run-tests.sh $(TEST_ARGS)
