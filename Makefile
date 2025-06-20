APPWRITE_CLI_TAG=latest

build_appwrite_cli:
	docker build -t appwrite-cli:$(APPWRITE_CLI_TAG) -f docker/Dockerfile.appwrite_cli ./docker

# push_appwrite_cli:
# 	docker tag appwrite-cli:latest appwrite-cli:$(APPWRITE_CLI_TAG)
# 	docker push appwrite-cli:$(APPWRITE_CLI_TAG)