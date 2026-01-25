AGENTS := researcher-agent

.PHONY: list
list:
	@echo $(AGENTS)

.PHONY: provision
provision:
	@echo "provision: use azd provision"

.PHONY: deploy
deploy:
	@echo "deploy: use azd deploy"

.PHONY: run test lint evals build
run test lint evals build:
	@if [ -z "$(AGENT)" ]; then \
		echo "Usage: make $@ AGENT=<agent>"; \
		exit 1; \
	fi
	$(MAKE) -C agents/$(AGENT) $@
