# push to github main branch before running this
# create an administrator role with credentials for configure
# run from the folder this file is in
aws configure
cdk bootstrap
poetry run cdk synth
poetry run cdk deploy