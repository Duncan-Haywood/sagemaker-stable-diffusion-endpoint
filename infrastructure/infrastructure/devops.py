from constructs import Construct
from aws_cdk import Stack, pipelines, Stage
from infrastructure.endpoint import EndpointStack
from aws_cdk import aws_codebuild as codebuild
from aws_cdk import aws_ecr as ecr

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
        asset_stage = AssetStage("AssetStage")
        general_image_uri = asset_stage.general_image_uri
        sagemaker_image_uri = asset_stage.sagemaker_image_uri

        self.pipeline.add_stage(asset_stage)

        self.pipeline.add_stage(
            EndpointStage(
                self, "TestStage", production=False, image_uri=sagemaker_image_uri
            ),
            pre=[unit_tests(general_image_uri)],
            post=[integration_tests(general_image_uri)],
        )

        self.pipeline.add_stage(
            EndpointStage(
                self, "ProdStage", production=True, image_uri=sagemaker_image_uri
            ),
            pre=[pipelines.ManualApprovalStep("PromoteToProd")],
            post=[integration_tests(general_image_uri)],
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
        self.repo = ecr.Repository(self, "Repository")
        image_repo_name = self.repo.repository_name
        self.repository_uri = self.repo.repository_uri
        pipelines.StackSteps(
            stack=self,
            post=[
                upload_image(image_repo_name, self.repository_uri, file_name, file_path)
            ],
        )


class AssetStage(Stage):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.general_docker_assets = AssetStack(self, "GeneralDockerECR")
        self.sagemaker_docker_assets = AssetStack(
            self, "SagemakerEndpointDocker", file_name="Dockerfile.endpoint"
        )
        # TODO the repo_uri might be different from the image uri, but probably works according to docs
        self.sagemaker_image_uri = self.general_docker_assets.repository_uri
        self.general_image_uri = self.sagemaker_docker_assets.repository_uri


class EndpointStage(Stage):
    def __init__(
        self, scope: Construct, construct_id: str, production: bool = False, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # create stacks
        self.app = EndpointStack(self, "EndpointStack")
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


def unit_tests(image_uri):
    return pipelines.CodeBuildStep(
        "UnitTest",
        commands=[
            "pytest --docker-local --upload-model -n $(nproc)",
        ],
        build_environment=codebuild.BuildEnvironment(
            privileged=True,
            compute_type=codebuild.ComputeType.LARGE,
            build_image=image_uri,
        ),
    )


def integration_tests(image_uri):
    return pipelines.CodeBuildStep(
        "UnitTest",
        commands=[
            "pytest --local-integration --integration -n $(nproc)",
        ],
        build_environment=codebuild.BuildEnvironment(
            privileged=True,
            compute_type=codebuild.ComputeType.LARGE,
            build_image=image_uri,
        ),
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
        cache=codebuild.Cache.local(codebuild.LocalCacheMode.DOCKER_LAYER),
    )
