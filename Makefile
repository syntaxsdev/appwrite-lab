APPWRITE_CLI_TAG=latest
APPWRITE_PLAYWRIGHT_TAG=latest

build_appwrite_cli:
	docker build -t appwrite-cli:$(APPWRITE_CLI_TAG) -f docker/Dockerfile.appwrite_cli ./docker


build_appwrite_playwright:
	docker build -t appwrite-playwright:$(APPWRITE_PLAYWRIGHT_TAG) -f docker/Dockerfile.appwrite_playwright ./docker

# push_appwrite_cli:
# 	docker tag appwrite-cli:latest appwrite-cli:$(APPWRITE_CLI_TAG)
# 	docker push appwrite-cli:$(APPWRITE_CLI_TAG)
clean-tests:
	appwrite-lab stop test-lab