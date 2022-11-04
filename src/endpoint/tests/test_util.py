from diffusion_util import util
import pytest
import moto
import boto3
from PIL import Image


@pytest.fixture
def secret_name():
    return "test"


@pytest.fixture
def secret_string():
    return "test"


def test_create_secret(secret_name, secret_string):
    response = util.create_secret(secret_name, secret_string)
    assert response is not None
    assert response["Name"] is not None


@pytest.fixture
def create_secret(secret_name, secret_string):
    response = util.create_secret(secret_name, secret_string)
    return response


def test_get_secret(secret_name, create_secret, secret_string):
    response = util.get_secret(secret_name)
    assert secret_string == response


def test_get_model_repository():
    model_repository = util.get_model_repository()
    assert model_repository is not None


def test_get_huggingface_secret_name():
    secret_name = util.get_huggingface_secret_name()
    assert secret_name is not None


@pytest.fixture
def bucket_name():
    return "test"


@pytest.fixture
def local_dir(tmp_path_factory):  # TODO
    path = tmp_path_factory.mktemp("test") / "test.txt"
    with open(path, "w") as f:
        f.write("test")
    return str(path)


@pytest.fixture
def key():
    return "test.txt"


def test_upload_file_to_s3(bucket_name, local_dir, key):
    with moto.mock_s3():
        s3 = boto3.resource("s3")
        bucket = s3.Bucket(bucket_name)
        bucket.create()
        util.upload_file_to_s3(bucket_name, local_dir, key)


def test_download_from_s3(bucket_name, local_dir, key):
    with moto.mock_s3():
        s3 = boto3.resource("s3")
        bucket = s3.Bucket(bucket_name)
        bucket.create()
        util.upload_file_to_s3(bucket_name, local_dir, key)
        util.download_from_s3(bucket_name, local_dir, key)


def test_get_model_bucket_name():
    result = util.get_model_bucket_name()
    assert result is not None


def test_get_model_s3_key():
    result = util.get_model_s3_key()
    assert result is not None


def test_get_model_repository():
    result = util.get_model_repository()
    assert result is not None


def test_get_huggingface_secret_name():
    result = util.get_huggingface_secret_name()
    assert result is not None


def test_get_config():
    config = util.get_config()
    assert config is not None


@pytest.fixture
def image():
    mode = "L"
    size = (512, 512)
    return Image.new(mode, size)


@pytest.fixture
def args(image):
    return [image, "test"]


@pytest.fixture
def kwargs():
    return dict(test="test")


def test_serialize_sagemaker_input(args, kwargs):
    response = util.serialize_sagemaker_input(*args, **kwargs)
    assert response is not None


@pytest.fixture
def bytesobj(args, kwargs):
    return util.serialize_sagemaker_input(*args, **kwargs)


def test_deserialize_sagemaker_input(bytesobj):
    response = util.deserialize_sagemaker_input(bytesobj)
    assert response is not None


@pytest.fixture
def response(image):
    return ([image], True)


def test_serialize_sagemaker_output(response):
    response = util.serialize_sagemaker_output(response)
    assert response is not None


@pytest.fixture
def output_bytesobj(response):
    return util.serialize_sagemaker_output(response)


def test_deserialize_sagemaker_output(output_bytesobj):
    response = util.deserialize_sagemaker_output(output_bytesobj)
    assert response is not None
