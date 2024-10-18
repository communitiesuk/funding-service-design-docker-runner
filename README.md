# Funding Service Design Runner

## Prerequisites
*  [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
*  All funding-service-design apps (listed as `context` keys in [docker-compose.yml](docker-compose.yml) must be checked out in the parent directory on this repository

## How to run
* Copy `.env.example` to `.env` and complete the missing values
  * `GOV_NOTIFY_API_KEY`: retrieve value of `GOV.UK Notify Test Key` from bitwarden vault
  * `AWS_XXX`: all these values can be found by connecting to cloudfoundry and running `cf service-key form-uploads-dev local-testing`
  * `AZURE_AD_*`: retrieve values from bitwarden vault - values named `AZURE AD TEST XXX`
* `docker compose up`
* Apps should be running on localhost on the ports in the [docker-compose.yml](docker-compose.yml) `ports` key before the `:`
* Note: When testing locally using the docker runner, docker might use the cached version of fsd_utils (or any another depedency). To avoid this and pick up your intended changes, run `docker compose build <service_name> --no-cache` first before running `docker compose up`.

## How to run in a GitHub codespace

* Go to https://github.com/communitiesuk/funding-service-design-docker-runner
* Click '< > Code ' -> '...' -> 'New with options' 
* Choose a 4-core machine and click start.
* Once VS Code has finished loading, open the command palette (Cmd+Shift+P) and type 'open workspace', then select 'funding-service-design-docker-runner/.devcontainer/funding-service-design-docker-runner.code-workspace'
* Create a file `.env` and populate it appropriately.
* In the terminal, run 'docker compose up'. Wait for everything to build and then go to the 'Ports' tab and click the URLs/browser buttons for Apply and Assess to open them in a new browser tab.

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
### Usage 1
Shell script to bulk clone git repositories from `https://github.com/communitiesuk`. Following repositories are cloned `("authenticator" "assessment" "assessment-store" "account-store" "application-store" "frontend" "fund-store" "notification" "digital-form-builder-adapter")`

        scripts/reset-all-repos.sh -f /path/to/workspace/dir

### Usage 2
Also used to go through each repo in turn, checkout the `main` branch and execute `git pull`. This is useful when you want to run the docker runner with the latest of all apps. Also optionally 'resets' the postgres image by forcefully removing it - useful if your local migrations get out of sync with the code or you need to start with a blank DB.

        scripts/reset-all-repos.sh -wm /path/to/workspace/dir

Where
- w: if supplied, will wipe the postgres image
- m: if supplied, will reset all repos to main
- f: if supplied, will do a git clone of FSD repos in workspace dir(make sure workspace dir has only docker-runner)
- path/to/workspace/dir: absolute path to your local directory where all the repos are checked out. Expects them all named the same as the git repos, eg. `funding-service-design-assessment-store`.

## install-venv-all-repos
Shell script to go through each repo in turn, create a virtual environment and install the dependencies. This is useful when you just started setting up and want to bulk create the virtual environments for all the repos, which reduces the manual effort of creating venv in each repo. Also optionally 'resets' the virtual environments by forcefully removing it - useful if you have issues with dependencies conflicts or change python versions or you need to start with a fresh setup.

        scripts/install-venv-all-repos.sh -vps /path/to/workspace/dir

Where
- v: if supplied, will wipe existing virtual environment & create a new one
- p: if supplied, will install pre-commit hooks
- s: if supplied, will build the static files in assessment, frontend & authenticator repos
- path/to/workspace/dir: absolute path to your local directory where all the repos are checked out. Expects them all named the same as the git repos, eg. `funding-service-design-assessment-store`.

To upgrade the depedencies, run the below command

        scripts/install-venv-all-repos.sh /path/to/workspace/dir


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
The form runner also runs in debug mode in docker compose, using the command `yarn runner startdebug`. There is a launch config inside the digital-form-builder-adapter repo called 'Docker Runner forms' - navigate to the debug view, select this configuration and launch the debugger. You can then set breakpoints in the typescript code to step through the runner code.

The debugger for the form-runner uses `nodemon` on port `9228` which is then exposed from the runner.

## localstack
LocalStack is a cloud service emulator that runs in a single container on your laptop or in your CI environment. With LocalStack, you can run your AWS applications or Lambdas entirely on your local machine without connecting to a remote cloud provider! Whether you are testing complex CDK applications or Terraform configurations, or just beginning to learn about AWS services, LocalStack helps speed up and simplify your testing and development workflow.

To add a new aws service in localstack, edit the env variable in localstack compose config.
```
- SERVICES=s3,sqs
```
If you experience any issues with localstack setup. Try below steps to resolve
1. Make the startup script `docker-localstack/setup-awslocal.sh` executable.

        chmod u+x docker-localstack/setup-awslocal.sh
2. Fix line ending on windows machine.

        sed -i -e 's/\r$//' docker-localstack/setup-awslocal.sh

3. If file upload doesn't work with an error like 'could not resolve host.docker.internal' make sure this is mapped in your `hosts` file. Sometimes this doesn't happen on install, but you can update it afterwards, more details [here](https://dluhcdigital.atlassian.net/wiki/spaces/FS/pages/79205102/Running+Access+Funding+Locally#localstack-on-Mac-OS---if-you-are-unable-to-update-your-hosts-file) (plus a workaround).

### AWS CLI in localstack
`aws` cli is available as `awslocal` in the localstack container. To access `awslocal` cli, bash into the localstack container.

        docker exec -it <localstacl_container_id> bash

Some useful commands
1. Display all SQS Queues - `awslocal sqs list-queues`
2. Create a Queue - `awslocal sqs create-queue --queue-name <queue_name>`
2. Below example demonstrates moving mesages to DLQ(Dead-letter-queue)
```bash
# Get queue attributes
awslocal sqs get-queue-attributes --queue-url http://localstack:4566/000000000000/import-queue.fifo --attribute-names All

# Send a Message
awslocal sqs send-message --queue-url http://localstack:4566/000000000000/import-queue.fifo --message-body "Hello, this is a test message" --delay-seconds 0 --message-group-id "test-group" --message-deduplication-id "test-deduplication"

# Receive a Message (trying to consume messages 3 times.)
for i in {1..6}; do
  sleep 1 # Waits 1 second.
  echo "iteration num $i"
  awslocal sqs receive-message --queue-url http://localstack:4566/000000000000/import-queue.fifo --attribute-names All --message-attribute-names All --max-number-of-messages 5 --wait-time-seconds 0 --visibility-timeout 0
done

# Check DLQ for transfered messages
awslocal sqs receive-message --queue-url http://localstack:4566/000000000000/import-dlq.fifo --attribute-names All --message-attribute-names All --max-number-of-messages 5 --wait-time-seconds 0 --visibility-timeout 0

# Message duplication test
awslocal sqs send-message --queue-url http://localstack:4566/000000000000/import-queue.fifo --message-body "Hello, this message is discarded as it's using previous message deduplication id" --delay-seconds 0 --message-group-id "test-group" --message-deduplication-id "test-deduplication"

```

## Gotchas
- If you can't connect, make sure you didn't get a port conflict error when running `docker compose up` - your environment may have different ports already in use.
- If breakpoints aren't working, make sure you didn't get a path mapping error when starting the apps - there's a chance the `pathMappings` element in the launch.json may need tweaking (aka `localRoot` for the form-runner config).
