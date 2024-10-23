# One Funding Service docker runner

This should walk you through getting set up with all Funding Service apps.

While this is in development (and maybe into the future), everything is cloned into the `./apps` dir of this repo, so shouldn't affect anything you already have in place. This docker compose also runs with a separate project name, so shouldn't affect any existing volumes/etc you have.

## Pre-requisites

* SSH keys set up with GitHub so that you can clone over SSH, not https. And access to all of the Funding Service repos.
* `pyenv` installed and integrated with your shell.

## How to get started

* Copy `.env.example` to `.env` and populate appropriately
* Update your `/etc/hosts` file to include the following lookups:
  * `127.0.0.1    one-submit-monitoring-data.levellingup.gov.localhost one-find-monitoring-data.levellingup.gov.localhost one-authenticator.levellingup.gov.localhost one-assessment.levellingup.gov.localhost one-frontend.levellingup.gov.localhost localstack host.docker.internal`
* Run `./scripts/reset-all-repos.sh -f` to git clone all repos into `./apps`
* Run `./scripts/install-venv-all-repos.sh -p -s` to create and populate venvs in all repos and install pre-commit hooks.
  * Note: there are some pre-existing issues with the script sometimes not picking the correct python version, may need some manual finagling until that is addressed.
* Run `make certs` to install a root certificate authority and generate appropriate certificates for our localhost domains.
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
* Run `make up` to start both pre- and post-award services, eg the entire Funding Service.
  * Or: `make pre up` (to just run pre-award services) or `make post up` (to just run post-award services)
  * Note: This will auto populate the fund-store DB and the post-award DB


## Service domains:

* Authenticator: https://one-authenticator.levellingup.gov.localhost:3004
  * Example: https://one-authenticator.levellingup.gov.localhost:3004/service/magic-links/new?fund=cof&round=r2w3

* Apply: https://one-frontend.levellingup.gov.localhost:3008
  * Example: https://one-frontend.levellingup.gov.localhost:3008/funding-round/cof/r2w3

* Assess: https://one-assessment.levellingup.gov.localhost:3010
  * Example: https://one-assessment.levellingup.gov.localhost:3010/assess/assessor_tool_dashboard/

* Find: https://one-find-monitoring-data.levellingup.gov.localhost:4001
  * Example: https://one-find-monitoring-data.levellingup.gov.localhost:4001/download

* Submit: https://one-submit-monitoring-data.levellingup.gov.localhost:4001
  * Example: https://one-submit-monitoring-data.levellingup.gov.localhost:4001/dashboard


========

Plus probably some steps from this repo's README.md and post-award-docker-runner's README.md...

Known things like this:
* .envrc in post-award-data-store repo for E2E test env vars
