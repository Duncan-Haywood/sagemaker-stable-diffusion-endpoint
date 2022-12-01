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
            synth=synth(source),
            code_build_defaults=pipelines.CodeBuildOptions(
                build_environment=codebuild.BuildEnvironment(
                    compute_type=codebuild.ComputeType.MEDIUM,
                ),
            ),
        )
        self.pipeline.add_stage(
            TestStage(self, "TestStage", production=False),
            pre=[
                unit_tests,
                docker_unit_tests,
                upload_model_tests,
            ],
            post=[],
        )
        self.pipeline.add_stage(
            CompleteStage(self, "IntegrationTestStage", production=False),
            post=[
                integration_tests,
            ],
        )

        self.pipeline.add_stage(
            CompleteStage(self, "ProdStage", production=True),
            pre=[pipelines.ManualApprovalStep("PromoteToProd")],
            post=[
                integration_tests,
            ],
        )


class TestStage(Stage):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # create model upload stack
        self.model_upload_stack = ModelUploadStack(self, "ModelUploadStack")
        # export variable
        self.lambda_function_name = self.model_upload_stack.lambda_function_name
        # steps for post
        pipelines.StackSteps(
            stack=self.model_upload_stack,
            post=[upload_model_trigger_step(self.lambda_function_name)],
        )


class AppStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # create model upload stack + export variables
        self.model_upload_stack = ModelUploadStack(self, "ModelUploadStack")
        model_bucket_name = self.model_upload_stack.model_bucket_name
        self.lambda_function_name = self.model_upload_stack.lambda_function_name

        # create endpoint stack
        self.endpoint_stack = EndpointStack(
            self, "EndpointStack", model_bucket_name=model_bucket_name
        )
        # might need because of dependency on bucket being created already?
        # self.endpoint_stack.add_dependency(self.model_upload_stack)

        # export variables
        self.endpoint_name = CfnOutput(
            self.endpoint_stack, "Output", value=self.endpoint_stack.endpoint_name
        )


class CompleteStage(Stage):
    def __init__(
        self, scope: Construct, construct_id: str, production: bool = False, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # create stacks
        self.app = AppStack(self, "CompleteApp")
        # add post processing steps
        pipelines.StackSteps(
            stack=self.app,
            post=[
                upload_model_trigger_step(self.app.lambda_function_name),
                set_endpoint_in_parameter_store(production, self.app.endpoint_name),
            ],
        )


## variables and functions referenced above
def synth(source):
    return pipelines.CodeBuildStep(
        "Synth",
        input=source,
        commands=[
            "cd infrastructure",
            "pip install poetry",
            "poetry install",
            "npm install -g aws-cdk",
            "poetry run cdk synth --output ../cdk.out",
        ],
    )


unit_tests = pipelines.CodeBuildStep(
    "UnitTest",
    commands=[
        "cd src/endpoint",
        "pip install poetry",
        "poetry install",
        "poetry run pytest",
    ],
)
docker_unit_tests = pipelines.CodeBuildStep(
    "DockerUnitTests",
    commands=[
        "cd src/endpoint",
        "pip install poetry",
        "poetry install",
        "poetry run pytest tests/test_docker.py --docker-local",
    ],
    build_environment=codebuild.BuildEnvironment(privileged=True),
)
upload_model_tests = pipelines.CodeBuildStep(
    "UploadModelTests",
    commands=[
        "cd src/endpoint",
        "pip install poetry",
        "poetry install",
        "poetry run pytest tests/test_upload_model.py --upload-model -n $(nproc)",
    ],
)
integration_tests = pipelines.CodeBuildStep(
    "IntegrationTest",
    commands=[
        "cd src/endpoint",
        "pip install poetry",
        "poetry install",
        "poetry run pytest tests/test_integration.py --integration",
    ],
)


def upload_model_trigger_step(lambda_function_name):
    step = pipelines.CodeBuildStep(
        "TriggerModelUploadLambda",
        commands=[
            "cd infrastructure",
            "pip install poetry",
            "poetry install",
            "poetry run python ./infrastructure/trigger_model_upload.py",
        ],
        env_from_cfn_outputs={"function_name": lambda_function_name},
    )
    return step


def set_endpoint_in_parameter_store(production, endpoint_name):
    step = pipelines.CodeBuildStep(
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
            "endpoint_name": endpoint_name,
        },
    )
    return step
