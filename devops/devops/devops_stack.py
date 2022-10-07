from constructs import Construct
from aws_cdk import Stack, pipelines


class PipelineStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        connection_arn = (
            "arn:aws:codestar-connections:us-east-1:219964407850:connection/68fc8f34-d233-40d3-a871-fa1b6195b9da"
        )  # TODO change to Stunn's
        owner_repo = "Duncan-Haywood/diffusion-endpoint"
        pipeline = pipelines.CodePipeline(
            self,
            "Pipeline",
            synth=pipelines.ShellStep(
                "Synth",
                input=pipelines.CodePipelineSource.connection(
                    owner_repo, "main", connection_arn=connection_arn
                ),
                commands=["npm ci", "npm run build", "npx cdk synth"],
            ),
        )
