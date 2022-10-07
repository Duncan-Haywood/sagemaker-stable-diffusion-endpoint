from aws_cdk import Stack

from constructs import Construct
from aws_cdk import aws_sagemaker as sagemaker


class EndpointInfrastructureStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
