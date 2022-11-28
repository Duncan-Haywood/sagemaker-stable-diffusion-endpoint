from aws_cdk import aws_s3 as s3
from aws_cdk import Stack, RemovalPolicy
from constructs import Construct
from aws_cdk import aws_lambda as lambda_


class ModelUploadStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        # model bucket for hosting the model files
        model_bucket = s3.Bucket(
            self,
            "ModelBucket",
            auto_delete_objects=True,
            removal_policy=RemovalPolicy.DESTROY,
        )
        # name of model bucket
        self.model_bucket_name = model_bucket.bucket_name

        # Dockerfile
        dockerfile_path = "../src/endpoint/"
        file = "Dockerfile.model_upload"
        model_code = lambda_.DockerImageCode.from_image_asset(
            dockerfile_path, file=file
        )
        # Lambda function
        # this may need to change because not large enough, but aws put a limit on it
        self.upload_model_lambda = lambda_.DockerImageFunction(
            self,
            "ModelUploadFn",
            code=model_code,
            memory_size=3008,
        )
        self.function_name = self.upload_model_lambda.function_name
