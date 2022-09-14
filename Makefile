.PHONY: format test

format: 
	black .

test:
	PYTHONPATH=./dnac_sidekick pytest --cov