aws configure
aws secretsmanager create-secret --name=hugging_face_hub_token --description="api token for use of hugging face model hub"
# cdk