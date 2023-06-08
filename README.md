# Funding Service Design Runner

## Prerequisites
*  [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
*  All funding-service-design apps (listed as `context` keys in [docker-compose.yml](docker-compose.yml) must be checked out in the parent directory on this repository

## How to run
* Copy `.env.example` to `.env` and ask another team member for the missing secret value
* `docker compose up`
* Apps should be running on localhost on the ports in the [docker-compose.yml](docker-compose.yml) `ports` key before the `:`
* Note: When testing locally using the docker runner, docker might use the cached version of fsd_utils (or any another depedency). To avoid this and pick up your intended changes, run `docker compose build <service_name> --no-cache` first before running `docker compose up`.

## Troubleshooting
* Check you have the `main` branch and latest revision of each repo checked out - see `reset-all-repos` script below
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

# Running in debug mode (VS Code)
## Python Apps
The containers in the docker runner can be run with python in debug mode to allow a debugger to connect. This gives instructions for connecting VS Code.

Each app in docker-compose has the following value for `command`, which makes the debugger run:

        command: ["sh", "-c", "python -m debugpy --listen 0.0.0.0:5678 -m flask run --no-debugger --host 0.0.0.0 --port 8080"]

The 'no-debugger' part relates to the flask debugger, it's useful to remove this option if you want to see the stack traces for things like jinja template errors.

To then expose the debug port 5678 to allow a debugger interface to connect, each app also needs a (unique) port mapping:

        ports:
                - 5681:5678

This allows you to then configure your chosen debugger (in this case VS code) to connect on that port. Add the following to the `configurations` block in the launch.json (if not already present) for the particular app you want to debug, where port matches the one exposes in docker-compose.


        {
            "name": "Docker runner",
            "type": "python",
            "request": "attach",
            "connect": {
                "host": "localhost",
                "port": 5681
            },
            "pathMappings": [
                {
                    "localRoot": "${workspaceFolder}",
                    "remoteRoot": "."
                }
            ],
            "justMyCode": true
        }

Save your launch.json, navigate to the debug view and select this new configuration from the drop down, then click the green triangle button to connect the debugger. Add some breakpoints and you should be able to step through the code executing in the docker runner.

## Form Runner
The form runner also runs in debug mode in docker compose, using the command `yarn runner startdebug`. There is a launch config inside the digital-form-builder repo called 'Docker Runner forms' - navigate to the debug view, select this configuration and launch the debugger. You can then set breakpoints in the typescript code to step through the runner code.

The debugger for the form-runner uses `nodemon` on port `9228` which is then exposed from the runner.

## Gotchas
- If you can't connect, make sure you didn't get a port conflict error when running `docker compose up` - your environment may have different ports already in use.
- If breakpoints aren't working, make sure you didn't get a path mapping error when starting the apps - there's a chance the `pathMappings` element in the launch.json may need tweaking (aka `localRoot` for the form-runner config).

