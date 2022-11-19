# push to github main branch before running this
# create an administrator role with credentials for configure
# run from the folder this file is in
# needs the aws cli installed
poetry install
echo "aws configure"
aws configure
echo "bootstrap"
poetry run cdk bootstrap
echo "synth"
poetry run cdk synth
echo "deploy"
poetry run cdk deploy