APPWRITE_CLI_TAG=latest
APPWRITE_PLAYWRIGHT_TAG=latest

build_appwrite_cli:
	docker build -t appwrite-cli:$(APPWRITE_CLI_TAG) -f docker/Dockerfile.appwrite_cli ./docker


build_appwrite_playwright:
	docker build -t appwrite-playwright:$(APPWRITE_PLAYWRIGHT_TAG) -f docker/Dockerfile.appwrite_playwright ./docker

# push_appwrite_cli:
# 	docker tag appwrite-cli:latest appwrite-cli:$(APPWRITE_CLI_TAG)
# 	docker push appwrite-cli:$(APPWRITE_CLI_TAG)
patch_templates:
	@VENV=$$(mktemp -d) && \
	uv venv $$VENV > /dev/null 2>&1 && \
	. $$VENV/bin/activate > /dev/null 2>&1 && \
	uv pip install ruamel.yaml > /dev/null 2>&1 && \
	python scripts/selinuxify_template_patch.py && \
	rm -rf $$VENV

tests:
	uv run pytest -rs -m e2e

clean-tests:
	@source .venv/bin/activate && \
	appwrite-lab stop test-lab

.PHONY: patch_templates tests clean-tests build_appwrite_cli build_appwrite_playwright