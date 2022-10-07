import aws_cdk as core
import aws_cdk.assertions as assertions
from devops.devops_stack import DevopsStack


def test_pipeline_created():
    app = core.App()
    stack = DevopsStack(app, "devops")
    template = assertions.Template.from_stack(stack)
