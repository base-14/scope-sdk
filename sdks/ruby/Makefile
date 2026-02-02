.PHONY: install test test-coverage lint lint-fix build release clean docs console ci all help pre-commit-install pre-commit

RUBY_VERSION := $(shell ruby -v 2>/dev/null | cut -d' ' -f2)
GEM_VERSION := $(shell ruby -e "require './lib/scope_client/version'; puts ScopeClient::VERSION" 2>/dev/null)

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	bundle install

test: ## Run tests
	bundle exec rspec

test-coverage: ## Run tests with coverage
	COVERAGE=true bundle exec rspec

lint: ## Run linter
	bundle exec rubocop

lint-fix: ## Run linter and auto-fix issues
	bundle exec rubocop -A

build: clean ## Build the gem
	gem build scope-client.gemspec

release: build ## Release to RubyGems (requires credentials)
	gem push scope-client-$(GEM_VERSION).gem

clean: ## Clean build artifacts
	rm -f *.gem
	rm -rf coverage/
	rm -rf doc/
	rm -rf .yardoc/

docs: ## Generate YARD documentation
	bundle exec yard doc

console: ## Start interactive console
	bundle exec bin/console

ci: lint test ## Run CI checks (lint + test)

all: install lint test build ## Run full build pipeline

pre-commit-install: ## Install pre-commit hooks (requires Python pre-commit)
	cd ../.. && pre-commit install

pre-commit: ## Run pre-commit on all files
	cd ../.. && pre-commit run --all-files
