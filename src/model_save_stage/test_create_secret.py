from . import create_secret
from botocore.stub import Stubber, ANY
import botocore.session


def test_get_env():
    env = create_secret.get_env()
    assert env["model_repository"] == "CompVis/stable-diffusion-v-1-4"


def test_create_secret():
    token = "test"
    response = create_secret.create_secret(token)
    assert response is not None
    assert response["Name"] is not None
