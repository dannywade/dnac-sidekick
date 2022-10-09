.PHONY: format test

format: 
	black . --check

test:
	pytest tests -v --cov=./dnac_sidekick