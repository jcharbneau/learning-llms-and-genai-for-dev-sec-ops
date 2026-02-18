DOCKER_COMPOSE ?= docker compose
SERVICE ?= notebooks
NOTEBOOK_PORT ?= 8888

.PHONY: help notebooks-build notebooks-up notebooks-down notebooks-logs notebooks-url notebooks-open

help:
	@echo "Targets:"
	@echo "  make notebooks-build  Build images"
	@echo "  make notebooks-up     Start notebooks and print login URL"
	@echo "  make notebooks-down   Stop and remove containers"
	@echo "  make notebooks-logs   Show recent notebooks logs"
	@echo "  make notebooks-url    Print latest Jupyter login URL"
	@echo "  make notebooks-open   Open latest Jupyter login URL in browser"

notebooks-build:
	$(DOCKER_COMPOSE) build

notebooks-up:
	$(DOCKER_COMPOSE) up -d
	@attempts=20; \
	url=""; \
	while [ $$attempts -gt 0 ]; do \
		url="$$( $(DOCKER_COMPOSE) logs --tail=80 $(SERVICE) 2>/dev/null | grep -Eo 'http://[^[:space:]]*:$(NOTEBOOK_PORT)/[^[:space:]]*token=[^[:space:]]+' | tail -n1 | sed -E 's|http://[^/:]+:|http://localhost:|' )"; \
		if [ -n "$$url" ]; then break; fi; \
		sleep 1; \
		attempts=$$((attempts-1)); \
	done; \
	if [ -n "$$url" ]; then \
		echo "Notebook URL: $$url"; \
	else \
		echo "Notebook URL not ready yet. Run: make notebooks-url"; \
	fi

notebooks-down:
	$(DOCKER_COMPOSE) down

notebooks-logs:
	$(DOCKER_COMPOSE) logs --tail=30 $(SERVICE)

notebooks-url:
	@url="$$( $(DOCKER_COMPOSE) logs --tail=120 $(SERVICE) 2>/dev/null | grep -Eo 'http://[^[:space:]]*:$(NOTEBOOK_PORT)/[^[:space:]]*token=[^[:space:]]+' | tail -n1 | sed -E 's|http://[^/:]+:|http://localhost:|' )"; \
	if [ -n "$$url" ]; then \
		echo "$$url"; \
	else \
		echo "No notebook URL found yet. Check startup logs with: make notebooks-logs"; \
		exit 1; \
	fi

notebooks-open:
	@url="$$( $(DOCKER_COMPOSE) logs --tail=120 $(SERVICE) 2>/dev/null | grep -Eo 'http://[^[:space:]]*:$(NOTEBOOK_PORT)/[^[:space:]]*token=[^[:space:]]+' | tail -n1 | sed -E 's|http://[^/:]+:|http://localhost:|' )"; \
	if [ -z "$$url" ]; then \
		echo "No notebook URL found yet. Check startup logs with: make notebooks-logs"; \
		exit 1; \
	fi; \
	if command -v open >/dev/null 2>&1; then \
		open "$$url"; \
	elif command -v xdg-open >/dev/null 2>&1; then \
		xdg-open "$$url"; \
	else \
		echo "Open this URL manually: $$url"; \
	fi
