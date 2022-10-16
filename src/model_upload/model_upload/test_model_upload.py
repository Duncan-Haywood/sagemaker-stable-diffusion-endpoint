from typeguard import is_typeddict
from . import upload_model
import pytest
from diffusion_util import util


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
def local_dir():
    return "./"


@pytest.fixture
def hugging_face_token(huggingface_secret_name):
    return util.get_secret(huggingface_secret_name)


@pytest.fixture
def model(model_id, hugging_face_token):
    return upload_model.load_model(model_id, hugging_face_token)


@pytest.mark.skip(reason="Large file download into RAM")
def test_load_model(model_id, hugging_face_token):
    model = upload_model.load_model(model_id, hugging_face_token)
    assert model is not None


@pytest.mark.skip(reason="Large file download into RAM")
def test_save_model_local(model, local_dir):
    response = upload_model.save_model_local(model, local_dir)


def test_get_config():
    d = upload_model.get_config()
    assert is_typeddict(d)
