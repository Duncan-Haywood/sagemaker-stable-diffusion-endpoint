# Usage

- you will need to change `OWNER_REPO` in the infrastructure/devops file at the top to your own repository

## undeploy

- to undeploy, see the undeploy.sh script and instructions there.

## deploy

- to deploy, first `poetry install; poetry run python ./endpoint/create_secret.py; poetry run python ./endpoint/github_token.py` in src/endpoint. and use your huggingface model hub token from your account. Then for the github token with the follwoing details: """Authentication will be done by a secret called `github-token` in AWS Secrets Manager (unless specified otherwise).The token should have these permissions: repo to read the repository and admin:repo_hook if you plan to use webhooks (true by default)""".
- then run deploy.sh from this file and see instructions in the comments in that file. push to github main branch before running this. create an administrator role with credentials when it asks. 

