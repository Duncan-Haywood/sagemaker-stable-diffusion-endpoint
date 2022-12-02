from infrastructure.endpoint import EndpointStack
from infrastructure.model_bucket import ModelBucketStack
from constructs import Construct
from aws_cdk import Stack, CfnOutput


class CompleteStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # create model upload stack
        self.model_upload_stack = ModelBucketStack(self, "ModelBucketStack")
        # export variables
        self.model_bucket_name = self.model_upload_stack.model_bucket_name

        # create endpoint stack
        self.endpoint_stack = EndpointStack(
            self, "EndpointStack", model_bucket_name=self.model_bucket_name
        )
        # might need because of dependency on bucket being created already?
        # self.endpoint_stack.add_dependency(self.model_upload_stack)

        # export variables
        self.endpoint_name = CfnOutput(
            self.endpoint_stack, "Output", value=self.endpoint_stack.endpoint_name
        )
