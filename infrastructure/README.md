# Usage

- you will need to change `OWNER_REPO` in the infrastructure/devops file at the top to your own repository

## undeploy

- to undeploy, see the undeploy.sh script and instructions there. there should be some secrets and roles and parameters and a pipeline which don't get torn down. Maybe some Docker containers in ECR, but I wouldn't think so. 

## deploy

- to deploy, first `poetry install; poetry run python ./endpoint/create_secret.py; poetry run python ./endpoint/upload_github_token.py` in src/endpoint. and use your huggingface model hub token from your account. Then for the github token with the follwoing details: """Authentication will be done by a secret called `github-token` in AWS Secrets Manager (unless specified otherwise).The token should have these permissions: repo to read the repository and admin:repo_hook if you plan to use webhooks (true by default)""".
- you may need to install the aws-cdk cli if not already on your computer.
- then run deploy.sh from this file and see instructions in the comments in that file. push to github main branch before running this. create an user with the policy attached: AdministratorAccess and programatic access credentials when it asks. After the pipeline is up and running, delete that user, as it is a security vulnerability.
- you need to increase service limit for ml.p2.xlarge to 1 or more for the service to work. and switch back INSTANCETYPE in endpoint.py to ml.p2.xlarge
- still might need an autoscaler added on the endpoint.
