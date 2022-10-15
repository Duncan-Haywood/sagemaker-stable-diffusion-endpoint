from . import util
import pytest


@pytest.fixture
def env():
    return util.get_env()


@pytest.fixture
def secret_name():
    return "test"


@pytest.fixture
def secret_string():
    return "test"


@pytest.fixture
def create_secret(secret_name, secret_string):
    response = util.create_secret(secret_name, secret_string)
    return response


def test_get_env():
    env = util.get_env()
    assert env["model_repository"] is not None


def test_create_secret(secret_name, secret_string):
    response = util.create_secret(secret_name, secret_string)
    assert response is not None
    assert response["Name"] is not None


def test_get_secret(secret_name, create_secret, secret_string):
    response = util.get_secret(secret_name)
    assert secret_string == response


def test_get_model_repository(env):
    model_repository = util.get_model_repository(env)
    assert model_repository is not None


def test_get_huggingface_secret_name(env):
    secret_name = util.get_huggingface_secret_name(env)
    assert secret_name is not None
