# Run the FastAPI server
include .env
export


dev:
	PYTHONPATH=./src uvicorn src.app:app --reload --host 0.0.0.0 --port $(PORT)

start:
	PYTHONPATH=./src uvicorn src.app:app --host 0.0.0.0 --port 8000

test:
	PYTHONPATH=./src pytest