.PHONY: help
help:             ## Show the help.
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@fgrep "##" Makefile | fgrep -v fgrep

.PHONY: run
run:             ## Show the help.
	uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

.PHONY: install
install:             ## Install the dependencies.
	pip install -r api/requirements.txt
