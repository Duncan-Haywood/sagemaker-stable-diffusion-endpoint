from constructs import Construct
from aws_cdk import Stack, pipelines, Stage
from .endpoint import EndpointStack

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
            synth=pipelines.ShellStep(
                "Synth",
                input=source,
                commands=[
                    "cd infrastructure",
                    "pip install poetry",
                    "poetry export -o requirements.txt",
                    "pip install -r requirements.txt",
                    "npm install -g aws-cdk",
                    "npx cdk synth",
                ],
            ),
        )
        self.pipeline.add_stage(
            EndpointStage(self, "TestStage"),
            post=[
                pipelines.ShellStep(
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
        self.pipeline.add_stage(
            EndpointStage(self, "ProdStage"),
            pre=[pipelines.ManualApprovalStep("PromoteToProd")],
        )


class EndpointStage(Stage):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.endpoint_stack = EndpointStack(self, "TestEndpointStack")
