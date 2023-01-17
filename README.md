# Funding Service Design Runner

## Prerequisites
*  [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
*  All funding-service-design apps (listed as `context` keys in [docker-compose.yml](docker-compose.yml) must be checked out in the parent directory on this repository

## How to run
* Copy `.env.example` to `.env` and ask another team member for the missing secret value
* `docker compose up`
* Apps should be running on localhost on the ports in the [docker-compose.yml](docker-compose.yml) `ports` key before the `:`

## Troubleshooting
* Check you have the `main` branch and latest revision of each repo checked out
* If dependencies have changed you may need to rebuild the docker images using `docker compose build`
* To run an individual app rather than all of them, run `docker compose up appname` where app name is the key defined under `services` in [docker-compose.yml](docker-compose.yml) 
* If you get an error about a database not existing, try running `docker compose down` followed by `docker compose up` this will remove and re-create any existing containers and volumes allowing the new databases to be created.
* If file upload is not working with an error about credentials, you need to uncomment lines 128 and 129 of `docker-compose.yml` and put the credentials in your `.env` file. The credentials are stored in the DLUHC BitWarden vault.


## Running e2e tests
To run the e2e tests against the docker runner, set the following env vars:

        export TARGET_URL_FRONTEND=http://localhost:3008
        export TARGET_URL_AUTHENTICATOR=http://localhost:3004
        export TARGET_URL_FORM_RUNNER=http://localhost:3009