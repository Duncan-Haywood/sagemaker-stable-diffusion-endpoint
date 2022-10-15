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
