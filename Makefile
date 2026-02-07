.PHONY: dev clear-db

dev:
	docker compose up --watch --build

clear-db:
	rm backend/database.db