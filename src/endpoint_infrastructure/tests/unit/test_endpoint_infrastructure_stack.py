import aws_cdk as core
import aws_cdk.assertions as assertions

from endpoint_infrastructure.endpoint_infrastructure_stack import (
    EndpointInfrastructureStack,
)

# example tests. To run these tests, uncomment this file along with the example
# resource in endpoint_infrastructure/endpoint_infrastructure_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = EndpointInfrastructureStack(app, "endpoint-infrastructure")
    template = assertions.Template.from_stack(stack)


#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
