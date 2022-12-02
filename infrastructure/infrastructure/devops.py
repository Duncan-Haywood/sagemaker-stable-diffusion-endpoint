from constructs import Construct
from aws_cdk import Stack, pipelines, Stage
from infrastructure.model_bucket import ModelBucketStack
from aws_cdk import aws_codebuild as codebuild
from infrastructure.complete import CompleteStack
from aws_cdk import aws_ecr as ecr
import os

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
        self.pipeline.add_stage(AssetStage("AssetStage"))
        self.test_wave = self.pipeline.add_wave("TestWave")
        self.test_wave.add_stage(
            TestStage(self, "TestStage"),
            pre=[
                unit_tests(),
                docker_unit_tests(),
                upload_model_tests(),
            ],
            post=[local_integration_tests()],
        )
        self.test_wave.add_stage(
            CompleteStage(self, "IntegrationTestStage", production=False),
            post=[integration_tests(), local_integration_tests()],
        )

        self.pipeline.add_stage(
            CompleteStage(self, "ProdStage", production=True),
            pre=[pipelines.ManualApprovalStep("PromoteToProd")],
            post=[integration_tests(), local_integration_tests()],
        )


class AssetStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        file_name="Dockerfile",
        file_path="src/endpoint",
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.general_endpoint_repo = ecr.Repository(self, "Repository")
        image_repo_name = self.general_endpoint_repo.repository_name
        self.repository_uri = self.general_endpoint_repo.repository_uri
        pipelines.StackSteps(stack = self, post=[upload_image(image_repo_name, self.repository_uri, file_name, file_path)])

class AssetStage(Stage):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.general_docker_assets = AssetStack(self, "GeneralDockerECR")


class TestStage(Stage):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # create model upload stack
        self.model_bucket = ModelBucketStack(self, "ModelBucketStack")
        pipelines.StackSteps(
            stack=self.model_bucket,
            post=[upload_model_step(self.model_bucket.model_bucket_name)],
        )


class CompleteStage(Stage):
    def __init__(
        self, scope: Construct, construct_id: str, production: bool = False, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # create stacks
        self.app = CompleteStack(self, "CompleteStack")
        # add post processing steps
        pipelines.StackSteps(
            stack=self.app,
            post=[
                upload_model_step(self.app.model_bucket_name),
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


# def all_unit_tests():
#     return pipelines.CodeBuildStep(
#         "UnitTest",
#         commands=[
#             "cd src/endpoint",
#             "pip install poetry",
#             "poetry install",
#             "poetry run pytest --docker-local --upload-model -n $(nproc)",
#         ],
#     )


def unit_tests():
    return pipelines.CodeBuildStep(
        "UnitTest",
        commands=[
            "cd src/endpoint",
            "pip install poetry",
            "poetry install",
            "poetry run pytest -n $(nproc)",
        ],
    )


def docker_unit_tests():
    return pipelines.CodeBuildStep(
        "DockerUnitTests",
        commands=[
            "cd src/endpoint",
            "pip install poetry",
            "poetry install",
            "poetry run pytest tests/test_docker_local.py --docker-local -n $(nproc)",
        ],
        build_environment=codebuild.BuildEnvironment(privileged=True),
    )


def upload_model_tests():
    return pipelines.CodeBuildStep(
        "UploadModelTests",
        commands=[
            "cd src/endpoint",
            "pip install poetry",
            "poetry install",
            "poetry run pytest tests/test_upload_model.py --upload-model -n $(nproc)",
        ],
    )


def local_integration_tests():
    return pipelines.CodeBuildStep(
        "LocalIntegrationTest",
        commands=[
            "cd src/endpoint",
            "pip install poetry",
            "poetry install",
            "poetry run pytest tests/test_local_integration.py --local-integration -n $(nproc)",
        ],
    )


def integration_tests():
    return pipelines.CodeBuildStep(
        "IntegrationTest",
        commands=[
            "cd src/endpoint",
            "pip install poetry",
            "poetry install",
            "poetry run pytest tests/test_integration.py --integration -n $(nproc)",
        ],
    )


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


def upload_model_step(model_bucket_name):
    return pipelines.CodeBuildStep(
        "UploadModel",
        commands=[
            "cd src/endpoint",
            "docker build --tag endpoint .",
            f"docker run --name endpoint -e 'model_bucket_name={model_bucket_name}' './endpoint/upload_model.py'",
        ],
    )


def upload_image(image_repo_name, repository_uri, file_name, file_path):
    return pipelines.CodeBuildStep(
        "Image",
        commands=[
            "docker build --tag $IMAGE_REPO_NAME --file $FILENAME $FILE_PATH",
            "docker tag $IMAGE_REPO_NAME $REPOSITORY_URI",
            "docker push $REPOSITORY_URI",
        ],
        build_environment=codebuild.BuildEnvironment(
            privileged=True, compute_type=codebuild.ComputeType.LARGE
        ),
        env=dict(
            IMAGE_REPO_NAME=image_repo_name,
            REPOSITORY_URI=repository_uri,
            FILENAME=file_name,
            FILE_PATH=file_path,
        ),
        cache=codebuild.Cache.local(codebuild.LocalCacheMode.DOCKER_LAYER)
    )
