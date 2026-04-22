.PHONY: help install init dev logs push clean

help:
	@echo "Snakky - IA Chat Makefile"
	@echo ""
	@echo "Available commands:"
	@echo "  make install    Install Python dependencies"
	@echo "  make init       Initialize database"
	@echo "  make dev        Run locally (reflex run)"
	@echo "  make db-reset   Reset database"
	@echo "  make logs       View Railway logs"
	@echo "  make push       Push to GitHub (git push)"
	@echo "  make clean      Clean cache & build files"

install:
	pip install -r requirements.txt

init:
	python -c "from snakky.db import init_db; import asyncio; asyncio.run(init_db())"

dev: init
	reflex run

db-reset:
	rm -f ./data/aiktivist.db
	python -c "from snakky.db import init_db; import asyncio; asyncio.run(init_db())"

logs:
	railway logs

push:
	git add -A
	git commit -m "$(msg)"
	git push

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .reflex -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
