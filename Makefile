.PHONY: dev-backend dev-frontend test lint migrate seed build

dev-backend:
	cd backend && .venv/bin/uvicorn app.main:app --reload --port 8000

dev-frontend:
	cd frontend && npm run dev

test:
	cd backend && .venv/bin/pytest tests/ -v

lint:
	cd backend && .venv/bin/ruff check . && cd ../frontend && npm run check

migrate:
	cd backend && .venv/bin/alembic upgrade head

seed:
	cd backend && .venv/bin/python ../dev/seed.py

build:
	cd frontend && npm run build
