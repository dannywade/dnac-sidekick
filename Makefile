.PHONY: format test install

format-check: 
	black . --check

format: 
	black .

test:
	pytest tests -v --cov=./dnac_sidekick

install:
	pip install -e .