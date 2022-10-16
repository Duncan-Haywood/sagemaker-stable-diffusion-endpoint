from . import model_from_hub_to_s3 as upload
import pytest
from . import util


@pytest.fixture
def env():
    return util.get_env()


@pytest.fixture
def model_id(env):
    return util.get_model_repository(env)


@pytest.fixture
def huggingface_secret_name(env):
    return util.get_huggingface_secret_name(env)


@pytest.fixture
def hugging_face_token(huggingface_secret_name):
    return util.get_secret(huggingface_secret_name)


@pytest.mark.skip(reason="Large file download into RAM")
def test_load_model(model_id, hugging_face_token):
    model = upload.load_model(model_id, hugging_face_token)
    assert model is not None
