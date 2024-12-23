SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c


.PHONY: certs
certs:
	mkdir -p certs
	CAROOT=certs mkcert -install
	CAROOT=certs mkcert -cert-file certs/cert.pem -key-file certs/key.pem "*.levellingup.gov.localhost"


# <-- Janky block to allow `make up` / `make pre up` / `make post up`, and same for `make ... down` -->
.PHONY: default
default:
	$(eval export COMPOSE_PROFILES=pre,post)


.PHONY: pre
pre: default
	$(eval export COMPOSE_PROFILES=pre)
	@true


.PHONY: post
post: default
	$(eval export COMPOSE_PROFILES=post)
	@true
# <-- Janky block to allow `make up` / `make pre up` / `make post up` -->


.PHONY: up
up: default
	docker compose up


.PHONY: down
down: default
	docker compose down

.PHONY: build
build: default
	docker compose build

.PHONY: clean-build
clean-build: default
	docker compose build --no-cache
