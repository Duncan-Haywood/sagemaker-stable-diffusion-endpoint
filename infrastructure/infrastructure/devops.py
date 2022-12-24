from constructs import Construct
from aws_cdk import Stack, pipelines, Stage, RemovalPolicy
from infrastructure.endpoint import EndpointStack
from aws_cdk import aws_codebuild as codebuild
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_iam as iam

OWNER_REPO = "Duncan-Haywood/diffusion-endpoint"
BRANCH = "v1"


class PipelineStack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, branch=BRANCH, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        source = pipelines.CodePipelineSource.git_hub(OWNER_REPO, branch)
        cache_bucket = s3.Bucket(
            self,
            "CacheBucket",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )
        synth_cache_bucket = s3.Bucket(
            self,
            "SynthCacheBucket",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )
        asset_cache_bucket = s3.Bucket(
            self,
            "AssetCacheBucket",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )
        self.pipeline = pipelines.CodePipeline(
            self,
            "Pipeline",
            synth=pipelines.CodeBuildStep(
                "Synth",
                input=source,
                install_commands=[
                    "npm install -g aws-cdk",
                    "pip install poetry",
                    "cd infrastructure",
                    "poetry install",
                ],
                commands=[
                    "cdk synth --output ../cdk.out",
                ],
            ),
            docker_enabled_for_self_mutation=True,
            code_build_defaults=pipelines.CodeBuildOptions(
                build_environment=codebuild.BuildEnvironment(
                    compute_type=codebuild.ComputeType.LARGE,
                    privileged=True,
                ),
                cache=codebuild.Cache.bucket(bucket=cache_bucket),
            ),
            synth_code_build_defaults=pipelines.CodeBuildOptions(
                build_environment=codebuild.BuildEnvironment(
                    compute_type=codebuild.ComputeType.MEDIUM,
                ),
                cache=codebuild.Cache.bucket(bucket=synth_cache_bucket),
            ),
            asset_publishing_code_build_defaults=pipelines.CodeBuildOptions(
                build_environment=codebuild.BuildEnvironment(
                    compute_type=codebuild.ComputeType.LARGE, privileged=True
                ),
                # cache=codebuild.Cache.local(codebuild.LocalCacheMode.DOCKER_LAYER),
                cache=codebuild.Cache.bucket(bucket=asset_cache_bucket),
            ),
        )
        # test stage
        test_stage = EndpointStage(
            self,
            "TestStage",
        )
        self.pipeline.add_stage(
            test_stage,
            pre=[unit_tests()],
            post=pipelines.Step.sequence(
                [
                    set_endpoint_in_parameter_store(
                        "False", test_stage.app.endpoint_name
                    ),
                    upload_model(test_stage.app.model_bucket_name),
                    integration_tests(production="False"),
                ]
            ),
        )
        # prod stage
        prod_stage = EndpointStage(
            self,
            "ProdStage",
        )
        self.pipeline.add_stage(
            prod_stage,
            pre=[pipelines.ManualApprovalStep("PromoteToProd")],
            post=pipelines.Step.sequence(
                [
                    set_endpoint_in_parameter_store(
                        "False", prod_stage.app.endpoint_name
                    ),
                    upload_model(prod_stage.app.model_bucket_name),
                    integration_tests(production="False"),
                ]
            ),
        )


class EndpointStage(Stage):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # create endpoint stack
        self.app = EndpointStack(self, "EndpointStack")


## functions referenced above


def unit_tests():
    return pipelines.CodeBuildStep(
        "UnitTest",
        install_commands=["pip install poetry", "cd src/endpoint", "poetry install"],
        commands=[
            "poetry run pytest -n $(nproc)",
        ],
        build_environment=codebuild.BuildEnvironment(
            privileged=True,
            compute_type=codebuild.ComputeType.LARGE,
        ),
    )


def integration_tests(production="True"):
    return pipelines.CodeBuildStep(
        "IntegrationTest",
        install_commands=["pip install poetry", "cd src/predict", "poetry install"],
        commands=[
            "poetry run pytest --integration",
        ],
        env={"production": production},
        build_environment=codebuild.BuildEnvironment(
            privileged=True,
            compute_type=codebuild.ComputeType.LARGE,
        ),
        role_policy_statements=[
            iam.PolicyStatement(actions=["ssm:GetParameter"], resources=["*"]),
            iam.PolicyStatement(actions=["s3:*"], resources=["*"]),
            iam.PolicyStatement(actions=["sagemaker:*"], resources=["*"]),
        ],
    )


def set_endpoint_in_parameter_store(production, endpoint_name):
    return pipelines.CodeBuildStep(
        "SetEndpointNameInParameterStore",
        install_commands=["pip install poetry", "cd src/util", "poetry install"],
        commands=[
            "poetry run python -m util.param_store_endpoint_name",
        ],
        build_environment=codebuild.BuildEnvironment(
            compute_type=codebuild.ComputeType.MEDIUM,
        ),
        env={
            "production": production,
        },
        env_from_cfn_outputs={
            "endpoint_name": endpoint_name,
        },
    )


def upload_model(model_bucket_name):
    return pipelines.CodeBuildStep(
        "UploadModel",
        install_commands=["pip install poetry", "cd src/endpoint", "poetry install"],
        commands=[
            "poetry run python -m endpoint.upload_model",
        ],
        build_environment=codebuild.BuildEnvironment(
            compute_type=codebuild.ComputeType.LARGE,
        ),
        env=dict(model_bucket_name=model_bucket_name),
    )
