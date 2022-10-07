# CICD pipeline

## instructions

To set up, use an account with administrator priveledges role attached to bootstrap with `cdk bootstrap`. Then remove those permissions for general security. Moving forward, use `cdk deploy` to create CI CD pipeline. To set up repository from which to run CICD, create a connection using https://docs.aws.amazon.com/dtconsole/latest/userguide/welcome-connections.html then change to your specifics: devops/devops_stack.py file - the variables: connection_arn and owner_repo.
