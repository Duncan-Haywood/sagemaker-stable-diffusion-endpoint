from endpoint import upload_model
import pytest
from endpoint import util
from moto import mock_s3
from logging import Logger

logger = Logger(__name__)

docker_mark = pytest.mark.skipif("not config.getoption('upload_model')")
pytestmark = docker_mark


@pytest.fixture
def model_id():
    return util.get_model_repository()


@pytest.fixture
def hugging_face_token():
    return util.get_hugging_face_token()


def test_load_model(model_id, hugging_face_token):
    model = upload_model.load_model(model_id, hugging_face_token)
    assert model is not None


@pytest.fixture
def model(model_id, hugging_face_token):
    return upload_model.load_model(model_id, hugging_face_token)


def test_save_model_local(model, tmp_path):
    local_dir = tmp_path
    upload_model.save_model_local(model, local_dir)


@pytest.fixture
def bucket_name_env(monkeypatch):
    monkeypatch.setenv("model_bucket_name", "test")


@pytest.mark.skip(reason="basically needs to rewrite main as setup")
def test_model_exists():
    raise NotImplementedError


def test_main(bucket_name_env):
    with mock_s3():
        upload_model.main()
