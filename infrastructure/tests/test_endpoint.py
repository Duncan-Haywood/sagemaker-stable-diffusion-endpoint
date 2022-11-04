from pyexpat import model
from infrastructure import endpoint
from aws_cdk.assertions import Template
import aws_cdk as cdk
import pytest


@pytest.fixture
def async_s3_output_path():
    return "test"  # TODO


@pytest.fixture
def model_name():
    return "test"  # TODO


@pytest.fixture
def execution_role_arn():
    return "test"  # TODO


@pytest.fixture
def model_bucket_name():
    return "test"


def test_EndpointStack():
    app = cdk.App()
    endpoint_stack = endpoint.EndpointStack(app, "Test")
    template = Template.from_stack(endpoint_stack)


def test_EndpointConfigConstruct(async_s3_output_path, model_name):
    stack = cdk.Stack()
    endpoint_config_construct = endpoint.EndpointConfigConstruct(
        stack, "Test", async_s3_output_path=async_s3_output_path, model_name=model_name
    )
    template = Template.from_stack(stack)


def test_ModelConstruct(execution_role_arn, model_bucket_name):
    stack = cdk.Stack()
    model_construct = endpoint.ModelConstruct(
        stack,
        "Test",
        model_bucket_name=model_bucket_name,
        execution_role_arn=execution_role_arn,
    )
    model = model_construct.model
    model_name = model.attr_model_name
    assert model is not None
    assert model_name is not None
    template = Template.from_stack(stack)
    template.has_resource("AWS::SageMaker::Model", {})


def test_ModelRoleConstruct():
    stack = cdk.Stack()
    model_role_stack = endpoint.ModelRoleConstruct(stack, "Test")
    template = Template.from_stack(stack)
