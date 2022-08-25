# Funding Service Design Runner

## Prerequisites
*  [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
*  All funding-service-design apps (listed as `context` keys in [docker-compose.yml](docker-compose.yml) must be checked out in the parent directory on this repository

## How to run
* Rename `.env.example` to `.env` and populate
* `docker compose up`
* Apps should be running on localhost on the ports in the [docker-compose.yml](docker-compose.yml) `ports` key before the `:`

## Troubleshooting
* Check you have the `main` branch and latest revision of each repo checked out
* If dependencies have changed you may need to rebuild the docker images using `docker compose build`
* To run an individual app rather than all of them, run `docker compose up appname` where app name is the key defined under `services` in [docker-compose.yml](docker-compose.yml) 
* If you get an error about a database not existing, try running `docker compose down` followed by `docker compose up` this will remove and re-create any existing containers and volumes allowing the new databases to be created.


