from . import create_secret
from botocore.stub import Stubber, ANY
import botocore.session
import pytest


def test_get_env():
    env = create_secret.get_env()
    assert env["model_repository"] == "CompVis/stable-diffusion-v-1-4"


def test_create_secret():
    token = "test"
    secret_name = "test"
    response = create_secret.create_secret(secret_name, token)
    assert response is not None
    assert response["Name"] is not None


def test_get_token_secret_name():
    env = create_secret.get_env()
    secret_name = create_secret.get_token_secret_name(env)
    assert secret_name is not None
