import aws_cdk as core
import aws_cdk.assertions as assertions
from devops.devops_stack import PipelineStack


def test_pipeline_created():
    app = core.App()
    stack = PipelineStack(app, "devops")
    template = assertions.Template.from_stack(stack)
    raise NotImplementedError