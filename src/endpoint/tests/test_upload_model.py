from endpoint import upload_model
import pytest
from endpoint import util
from moto import mock_s3


@pytest.fixture
def model_id():
    return util.get_model_repository()


@pytest.fixture
def huggingface_secret_name():
    return util.get_huggingface_secret_name()


@pytest.fixture
def hugging_face_token(huggingface_secret_name):
    return util.get_secret(huggingface_secret_name)


@pytest.mark.skip(reason="Large file download into RAM")
def test_load_model(model_id, hugging_face_token):
    model = upload_model.load_model(model_id, hugging_face_token)
    assert model is not None


@pytest.fixture
def local_dir():
    return "./"


@pytest.fixture
def model(model_id, hugging_face_token):
    return upload_model.load_model(model_id, hugging_face_token)


@pytest.mark.skip(reason="Large file download into RAM")
def test_save_model_local(model, local_dir):
    response = upload_model.save_model_local(model, local_dir)


@pytest.mark.skip(reason="Not implemented")
def test_get_config():
    d = upload_model.get_config()
    assert type(d) == dict


@pytest.mark.skip(reason="Large file download into RAM")
def test_main():
    with mock_s3():
        upload_model.main()
    raise NotImplementedError


@pytest.mark.skip(reason="Large file download into RAM")
def test_lambda_handler():
    upload_model.lambda_handler(None, None)
    raise NotImplementedError


@pytest.mark.skip(reason="Not implemented")
def test_model_exists():  # bucket_name, key)
    # model_exists(bucket_name, key)
    raise NotImplementedError
