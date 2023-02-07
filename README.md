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
* If file upload is not working with an error about credentials, you need to uncomment [these lines](https://github.com/communitiesuk/funding-service-design-docker-runner/blob/d13af481818fbd6398c3583e49a33edd6fb19496/docker-compose.yml#L114-L116) in `docker-compose.yml` and put the credentials in your `.env` file. The credentials are stored in the DLUHC BitWarden vault.


## Running e2e tests
To run the e2e tests against the docker runner, set the following env vars:

        export TARGET_URL_FRONTEND=http://localhost:3008
        export TARGET_URL_AUTHENTICATOR=http://localhost:3004
        export TARGET_URL_FORM_RUNNER=http://localhost:3009

## Debugging

All the services in docker-compose now include the following in their config:

`command: ["sh", "-c", "pip install debugpy -t /tmp && python /tmp/debugpy --listen 0.0.0.0:5678 -m flask run --no-debugger --no-reload --host 0.0.0.0 --port 8080"]`

    ports:
      - <unique debug port>:5678
      - <another port>:8080

The use of `debugpy` starts a debug listener on port `5678` - this is then running whether you connect to it or not. If you want to attach a debugger to that listener, follow instructions below. Each service must expose the debug listener on port 5678 to its own unique port, otherwise they will clash.

To attach a debugger in VS Code for a particular service, add the following to the `launch.json` for your chosen app, making sure the port matches the exposed debug port in `docker-compose.yml`.

        {
            "name": "Python: Remote Attach",
            "type": "python",
            "request": "attach",
            "connect": {
                "host": "localhost",
                "port": 5684
            },
            "pathMappings": [
                {
                    "localRoot": "${workspaceFolder}",
                    "remoteRoot": "."
                }
            ],
            "justMyCode": true
        },