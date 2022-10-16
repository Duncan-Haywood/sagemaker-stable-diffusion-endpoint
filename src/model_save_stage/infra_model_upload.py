from aws_cdk import aws_s3 as s3
from aws_cdk import Stack
import typing
from constructs import Construct
from aws_cdk import aws_lambda as lambda_


class ModelSaveStack(Stack):
    def __init__(
        self,
        scope: typing.Optional[Construct] = None,
        id: typing.Optional[str] = None,
        **kwargs
    ) -> None:

        super().__init__(scope, id, **kwargs)

        model_bucket = s3.Bucket(self, "Modelbucket")
        upload_model_lambda = ModelLambdaConstruct()


class ModelLambdaConstruct(Construct):
    def __init__(self, scope: Construct, id: str) -> None:
        super().__init__(scope, id)

        dockerfile_path = "./"
        model_code = lambda_.DockerImageCode.from_asset_image(dockerfile_path)
        upload_model_lambda = lambda_.DockerImageFunction(
            self,
            "ModelUploadFn",
            code=model_code,
            runtime=lambda_.Runtime.PYTHON_3_9,
            memory_size=10240,
            # tracing=lambda_.Tracing.ACTIVE,
            # profiling=True,
            # vpc=None,
            # vpc_subnets=None,
        )
        return upload_model_lambda
