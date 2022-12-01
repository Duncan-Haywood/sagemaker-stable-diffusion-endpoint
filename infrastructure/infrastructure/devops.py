from constructs import Construct
from aws_cdk import Stack, pipelines, Stage, CfnOutput
from infrastructure.endpoint import EndpointStack
from infrastructure.model_upload import ModelUploadStack
from aws_cdk import aws_codebuild as codebuild

OWNER_REPO = "Duncan-Haywood/diffusion-endpoint"
BRANCH = "main"


class PipelineStack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, branch=BRANCH, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        source = pipelines.CodePipelineSource.git_hub(OWNER_REPO, branch)
        self.pipeline = pipelines.CodePipeline(
            self,
            "Pipeline",
            synth=pipelines.CodeBuildStep(
                "Synth",
                input=source,
                commands=[
                    "cd infrastructure",
                    "pip install poetry",
                    "poetry install",
                    "npm install -g aws-cdk",
                    "poetry run cdk synth --output ../cdk.out",
                ],
            ),
            code_build_defaults=pipelines.CodeBuildOptions(
                build_environment=codebuild.BuildEnvironment(
                    compute_type=codebuild.ComputeType.MEDIUM,
                ),
            ),
        )
        self.pipeline.add_stage(
            EndpointStage(self, "TestStage", production=False),
            pre=[
                pipelines.CodeBuildStep(
                    "UnitTest",
                    commands=[
                        "cd src/endpoint",
                        "pip install poetry",
                        "poetry install",
                        "poetry run pytest",
                    ],
                ),
                pipelines.CodeBuildStep(
                    "DockerUnitTests",
                    commands=[
                        "cd src/endpoint",
                        "pip install poetry",
                        "poetry install",
                        "poetry run pytest tests/test_docker.py --docker-local",
                    ],
                    build_environment=codebuild.BuildEnvironment(privileged=True),
                ),
            ],
            post=[
                pipelines.CodeBuildStep(
                    "IntegrationTest",
                    commands=[
                        "cd src/endpoint",
                        "pip install poetry",
                        "poetry install",
                        "poetry run pytest tests/test_integration.py --integration",
                    ],
                ),
            ],
        )
        self.pipeline.add_stage(
            EndpointStage(self, "ProdStage", production=True),
            pre=[pipelines.ManualApprovalStep("PromoteToProd")],
            post=[
                pipelines.CodeBuildStep(
                    "IntegrationTest",
                    commands=[
                        "cd src/endpoint",
                        "pip install poetry",
                        "poetry install",
                        "poetry run pytest --integration",
                    ],
                ),
            ],
        )


class EndpointStage(Stage):
    def __init__(
        self, scope: Construct, construct_id: str, production: bool = False, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # model upload
        self.model_upload_stack = ModelUploadStack(self, "ModelUploadStack")
        model_bucket_name = self.model_upload_stack.model_bucket_name
        lambda_function_name = CfnOutput(
            self.model_upload_stack,
            "Output",
            value=self.model_upload_stack.function_name,
        )
        # upload the model after the infrastructure for the lambda is deployed
        pipelines.StackSteps(
            stack=self.model_upload_stack,
            post=[
                pipelines.CodeBuildStep(
                    "TriggerModelUploadLambda",
                    commands=[
                        "cd infrastructure",
                        "pip install poetry",
                        "poetry install",
                        "poetry run python ./infrastructure/trigger_model_upload.py",
                    ],
                    env_from_cfn_outputs={"function_name": lambda_function_name},
                )
            ],
        )
        # infrastructure for the endpoint
        self.endpoint_stack = EndpointStack(
            self, "EndpointStack", model_bucket_name=model_bucket_name
        )
        self.endpoint_stack.add_dependency(self.model_upload_stack)
        self.endpoint_name = CfnOutput(
            self.endpoint_stack, "Output", value=self.endpoint_stack.endpoint_name
        )
        pipelines.StackSteps(
            stack=self.model_upload_stack,
            post=[
                pipelines.CodeBuildStep(
                    "SetEndpointNameInParameterStore",
                    commands=[
                        "cd infrastructure",
                        "pip install poetry",
                        "poetry install",
                        "poetry run python ./infrastructure/param_store_endpoint_name.py",
                    ],
                    env={
                        "production": str(production),
                    },
                    env_from_cfn_outputs={
                        "endpoint_name": self.endpoint_name,
                    },
                )
            ],
        )
