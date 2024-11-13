#!/bin/bash

echo "............Creating pre_award_stores database............"
docker compose exec database psql postgresql://postgres:password@database:5432/fund_store -c 'CREATE DATABASE pre_award_stores;' # pragma: allowlist secret
docker compose exec database psql postgresql://postgres:password@database:5432/fund_store -c 'CREATE DATABASE pre_award_stores_test;' # pragma: allowlist secret

echo "............Creating pre-award-stores image and running database migrations............"
docker compose up -d pre-award-stores
docker compose exec pre-award-stores flask db upgrade

echo "............Truncate any existing data in pre_award_stores database............"
docker compose exec database psql postgresql://postgres:password@database:5432/pre_award_stores -c 'truncate table assessment_field cascade;' # pragma: allowlist secret
docker compose exec database psql postgresql://postgres:password@database:5432/pre_award_stores -c 'truncate table fund cascade;' # pragma: allowlist secret
docker compose exec database psql postgresql://postgres:password@database:5432/pre_award_stores -c 'truncate table round cascade;' # pragma: allowlist secret
docker compose exec database psql postgresql://postgres:password@database:5432/pre_award_stores -c 'truncate table section cascade;' # pragma: allowlist secret
docker compose exec database psql postgresql://postgres:password@database:5432/pre_award_stores -c 'truncate table section_field cascade;' # pragma: allowlist secret
docker compose exec database psql postgresql://postgres:password@database:5432/pre_award_stores -c 'truncate table event cascade;' # pragma: allowlist secret
docker compose exec database psql postgresql://postgres:password@database:5432/pre_award_stores -c 'truncate table form_name cascade;' # pragma: allowlist secret

echo "............Copying data from fund_store to pre_award_stores............"
docker compose exec database bash -c "pg_dump --verbose --data-only --format custom --exclude-table alembic_version postgresql://postgres:password@database:5432/fund_store | pg_restore --verbose --data-only --format custom --dbname postgresql://postgres:password@database:5432/pre_award_stores" # pragma: allowlist secret
