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
* If file upload is not working with an error about credentials, you need to uncomment [these lines](https://github.com/communitiesuk/funding-service-design-docker-runner/blob/d13af481818fbd6398c3583e49a33edd6fb19496/docker-compose.yml#L114-L116) in `docker-compose.yml` and put the credentials in your `.env` file. The credentials are stored in the DLUHC BitWarden vault. (Same applies for file uploads in assessment or SSO in authentication for example.)


## Running e2e tests
To run the e2e tests against the docker runner, set the following env vars:

        export TARGET_URL_FRONTEND=http://localhost:3008
        export TARGET_URL_AUTHENTICATOR=http://localhost:3004
        export TARGET_URL_FORM_RUNNER=http://localhost:3009

# Scripts
## reset-all-repos
Shell script to go through each repo in turn, checkout the `main` branch and execute `git pull`. This is useful when you want to run the docker runner with the latest of all apps. Also optionally 'resets' the postgres image by forcefully removing it - useful if your local migrations get out of sync with the code or you need to start with a blank DB.

        scripts/reset-all-repos.sh -wm /path/to/workspace/dir

Where
- w: if supplied, will wipe the postgres image
- m: if supplied, will reset all repos to main
- path/to/workspace/dir: absolute path to your local directory where all the repos are checked out. Expects them all named the same as the git repos, eg. `funding-service-design-assessment-store`.