# Funding Service Design Runner

## Pre-requisite software
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
* SSH keys set up with GitHub so that you can clone over SSH, not https. And access to all of the Funding Service repos.
* [`pyenv`](https://github.com/pyenv/pyenv) installed and integrated with your shell. Install Python 3.10 and 3.11.
* [`nvm`](https://github.com/nvm-sh/nvm) installed.
  * Install Yarn globally with `npm i -g yarn`.
* [`mkcert`](https://github.com/FiloSottile/mkcert) installed.

## Required setup
1. Copy `.env.example` to `.env` and fill in any required missing values.
2. Edit your `/etc/hosts` file and add the following line at the end:
  * `127.0.0.1    submit-monitoring-data.levellingup.gov.localhost find-monitoring-data.levellingup.gov.localhost authenticator.levellingup.gov.localhost assessment.levellingup.gov.localhost frontend.levellingup.gov.localhost localstack host.docker.internal`
3. Run `./scripts/reset-all-repos.sh -f` to git clone all repos into `./apps`
4. Run `./scripts/install-venv-all-repos.sh -v -p -s` to create and populate venvs in all repos and install pre-commit hooks.
  * Note: there are some pre-existing issues with the script sometimes not picking the correct python version, may need some manual finagling until that is addressed.
5. Run `make certs` to install a root certificate authority and generate appropriate certificates for our localhost domains.
  * If you are on a MHCLG laptop, your default user is unlikely to have `sudo` permission, which is required, so you may need to take the following steps instead:
    * Find your STANDARD_USER (that you use normally) and ADMIN_USER (that can use `sudo`) account names. Substitute appropriately in the following commands:
    * `su - <ADMIN_USER>`
    * `cd` to the directory *above* this docker-runner repo.
    * run `sudo chown -R <ADMIN_USER>:staff funding-service-design-docker-runner`
    * `cd funding-service-design-docker-runner`
    * `make certs`  # Read the output - should be no apparent errors.
    * `cd ..`
    * `sudo chown -R <STANDARD_USER>:staff funding-service-design-docker-runner`
    * `exit` to return to your standard user shell.
  * If you hit the error `SecTrustSettingsSetTrustSettings: The authorization was denied since no user interaction was possible.` when doing the above `su -` steps, then you may need to actually logout and login as your admin user instead of using `su`

## Running the Funding Service

Depending on which part(s) of the Funding Service you wish to run, you have a few options.

To run everything, execute `make up`.

To run just the pre-award services, execute `make pre up`.

To run just the post-award services, execute `make post up`.


### Service domains:

* Authenticator: https://authenticator.levellingup.gov.localhost:3004
  * Example URL: https://authenticator.levellingup.gov.localhost:3004/service/magic-links/new?fund=cof&round=r2w3

* Apply: https://frontend.levellingup.gov.localhost:3008
  * Example URL: https://frontend.levellingup.gov.localhost:3008/funding-round/cof/r2w3

* Assess: https://assessment.levellingup.gov.localhost:3010
  * Example URL: https://assessment.levellingup.gov.localhost:3010/assess/assessor_tool_dashboard/

* Find: https://find-monitoring-data.levellingup.gov.localhost:4001
  * Example URL: https://find-monitoring-data.levellingup.gov.localhost:4001/download

* Submit: https://submit-monitoring-data.levellingup.gov.localhost:4001
  * Example URL: https://submit-monitoring-data.levellingup.gov.localhost:4001/dashboard

## Troubleshooting
* Check you have the `main` branch and latest revision of each repo checked out - see the `reset-all-repos` section below
* If dependencies have changed you may need to rebuild the docker images using `make build`
* To run an individual app rather than all of them, run `docker compose up <appname>` where app name is the key defined under `services` in [docker-compose.yml](docker-compose.yml)
* If you get an error about a database not existing, try running `make down` followed by `make up`. This will remove and re-create any existing containers and volumes allowing the new databases to be created.


## Running e2e tests
To run the e2e tests against the docker runner, set the following env vars:

        export TARGET_URL_FRONTEND=https://frontend.levellingup.gov.localhost:3008
        export TARGET_URL_AUTHENTICATOR=https://authenticator.levellingup.gov.localhost:3004
        export TARGET_URL_FORM_RUNNER=https://form-runner.levellingup.gov.localhost:3009

# Scripts
## reset-all-repos
### Usage 1
Shell script to bulk clone the core Funding Service git repositories from `https://github.com/communitiesuk`.

        scripts/reset-all-repos.sh -f

### Usage 2
Also used to go through each repo in turn, checkout the `main` branch and execute `git pull`. This is useful when you want to run the docker runner with the latest of all apps.

        scripts/reset-all-repos.sh -fml

Where
- f: if supplied, will do a git clone of FSD repos into the `apps` subdirectory.
- m: if supplied, will reset all repos to main
- l: if supplied, will show the latest commit hash for each repo

## install-venv-all-repos
Shell script to go through each repo in turn, create a virtual environment and install the dependencies. This is useful when you just started setting up and want to bulk create the virtual environments for all the repos, which reduces the manual effort of creating venv in each repo. Also optionally 'resets' the virtual environments by forcefully removing it - useful if you have issues with dependencies conflicts or change python versions or you need to start with a fresh setup.

        scripts/install-venv-all-repos.sh -vps

Where
- v: if supplied, will wipe existing virtual environment & create a new one
- p: if supplied, will install pre-commit hooks
- s: if supplied, will build the static files for services that serve HTML.


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
- If you can't connect, make sure you didn't get a port conflict error when running `make up` - your environment may have different ports already in use.
- If breakpoints aren't working, make sure you didn't get a path mapping error when starting the apps - there's a chance the `pathMappings` element in the launch.json may need tweaking (aka `localRoot` for the form-runner config).
