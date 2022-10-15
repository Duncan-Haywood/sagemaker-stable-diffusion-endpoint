from . import util


def test_get_env():
    env = util.get_env()
    assert env["model_repository"] is not None


def test_create_secret():
    secret_string = "test"
    secret_name = "test"
    response = util.create_secret(secret_name, secret_string)
    assert response is not None
    assert response["Name"] is not None


def test_get_secret():
    secret_string = "test"
    secret_name = "test"
    util.create_secret(secret_name, secret_string)
    response = util.get_secret(secret_name)
    assert secret_name == response


def test_get_model_repository():
    env = util.get_env()
    model_repository = util.get_model_repository(env)
    assert model_repository is not None


def test_get_huggingface_secret_name():
    env = util.get_env()
    secret_name = util.get_huggingface_secret_name(env)
    assert secret_name is not None
