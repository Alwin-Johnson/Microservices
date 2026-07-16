# ==============================================================================
# restore-platform-stability — Makefile
#
# Provides developer convenience targets for building, running, and managing
# the platform locally via Docker Compose.
#
# Usage:
#   make build       Build all service images
#   make up          Start all containers
#   make down        Stop and remove containers
#   make logs        Tail all container logs
#   make ps          Show running container status
#   make clean       Remove images, volumes, and containers
# ==============================================================================

# Use bash for all shell commands
SHELL := /bin/bash

# Docker host — uses podman socket for rootless operation if available,
# falls back to the system Docker socket.
PODMAN_SOCK := /run/user/$(shell id -u)/podman/podman.sock
DOCKER_SOCK := /var/run/docker.sock

ifneq ("$(wildcard $(PODMAN_SOCK))","")
  DOCKER_HOST := unix://$(PODMAN_SOCK)
else
  DOCKER_HOST := unix://$(DOCKER_SOCK)
endif

export DOCKER_HOST

COMPOSE := docker compose

.PHONY: help build up down restart logs ps clean build-no-cache

# Default target
help: ## Show this help message
	@echo "restore-platform-stability — available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

build: ## Build all service images
	$(COMPOSE) build

build-no-cache: ## Build all service images without cache
	$(COMPOSE) build --no-cache

up: ## Start all containers in the background
	$(COMPOSE) up -d

down: ## Stop and remove containers (preserves volumes)
	$(COMPOSE) down

restart: ## Restart all containers
	$(COMPOSE) restart

logs: ## Tail logs for all containers
	$(COMPOSE) logs -f

logs-%: ## Tail logs for a specific service (e.g. make logs-orders)
	$(COMPOSE) logs -f $*

ps: ## Show container status
	$(COMPOSE) ps

clean: ## Remove all containers, images, and volumes (destructive)
	$(COMPOSE) down --volumes --remove-orphans
	$(COMPOSE) rm -f
