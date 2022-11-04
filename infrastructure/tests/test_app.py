from infrastructure import app
from aws_cdk.assertions import Template
import pytest


def test_main():
    app.main()


def template_jsons(metafunc):
    cloud_assembly = app.main()
    stacks = cloud_assembly.stacks  # type List[CloudFormationStackArtifact]
    templates = [stack.template for stack in stacks]
    template_jsons = [template.to_json() for template in templates]
    return template_jsons


# The snapshot parameter is injected by Pytest -- it's a fixture provided by
# syrupy, the snapshot testing library we're using:
# https://docs.pytest.org/en/stable/fixture.html
# @pytest.mark.parametrize("json", template_jsons())
# def test_main_snapshot(json, snapshot):
#     assert json == snapshot
