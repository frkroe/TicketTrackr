#!/usr/bin/make -f

PROJECT_NAME := tickettrackr

.PHONY: install-test-requirements test linting build
.PHONY: env-start env-stop env-recreate docker-cleanup bash shell init

ROOT_FOLDER := $(shell pwd)
DOCKER_COMPOSE_FILE := $(ROOT_FOLDER)/docker/docker-compose.yml
DOCKER_PROJECT_NAME := $(PROJECT_NAME)-extract-load
DOCKER_DEPENDENCIES_IMAGE := mimove/$(DOCKER_PROJECT_NAME)-base-dependecies
DOCKER_DEPENDENCIES_IMAGE_VERSION := 1
DEPENDENCIES_DOCKERFILE := docker/Dockerfile.dependencies
DOCKER_COMMAND := docker-compose -p $(DOCKER_PROJECT_NAME) -f $(DOCKER_COMPOSE_FILE)


ifeq ($(DOCKER_IMAGE_NAME),)
export DOCKER_IMAGE_NAME := $(PROJECT_NAME)
endif

ifeq ($(DOCKER_IMAGE_TAG),)
export DOCKER_IMAGE_TAG := latest
endif

ifeq ($(DOCKER_BRANCH_NAME),)
export DOCKER_BRANCH_NAME := local
endif

install-test-requirements: ## Install all test dependencies
	$(DOCKER_COMMAND) exec -T service pip3 install --disable-pip-version-check -r /app/requirements/test.txt

sort-imports: ## Sort imports
	$(DOCKER_COMMAND) exec -T service isort -rc -y .

test: build env-start install-test-requirements ## Run test suite for inference in project's main container
	$(DOCKER_COMMAND) exec -T service /app/scripts/test-command.sh

linting: build env-start install-test-requirements ## Check/Enforce Python Code-Style
	$(DOCKER_COMMAND) exec -T service /app/scripts/lint-command.sh $(LINTFLAGS)

build: ## Build project image
	$(DOCKER_COMMAND) build

build-base-image: ## Build base image
	docker build -t $(DOCKER_DEPENDENCIES_IMAGE):$(DOCKER_DEPENDENCIES_IMAGE_VERSION) -f $(DEPENDENCIES_DOCKERFILE) .

push-base-image: ## Push base image
	docker push $(DOCKER_DEPENDENCIES_IMAGE):$(DOCKER_DEPENDENCIES_IMAGE_VERSION)

env-start: ## Start project containers defined in docker-compose
	$(DOCKER_COMMAND) up -d

env-stop: ## Stop project containers defined in docker-compose
	$(DOCKER_COMMAND) stop

env-destroy: ## Destroy all project containers
	$(DOCKER_COMMAND) down -v --rmi all --remove-orphans

env-recreate: build env-start install-test-requirements ## Force building project image and start all containers again

env-reset: destroy-containers env-start install-test-requirements ## Destroy project containers and start them again

destroy-containers: ## Destroy project containers
	$(DOCKER_COMMAND) down -v

docker-cleanup: ## Purge all Docker images in the system
	$(DOCKER_COMMAND) down -v
	docker system prune -f

bash: ## Open a bash shell in project's main container
	$(DOCKER_COMMAND) exec service bash

view-logs: ## Show logs
	$(DOCKER_COMMAND) logs -f