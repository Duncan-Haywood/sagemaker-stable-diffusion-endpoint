import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--integration",
        action="store_true",
        dest="integration",
        default=False,
        help="enable integration decorated tests",
    )
    parser.addoption(
        "--docker-local",
        action="store_true",
        dest="docker_local",
        default=False,
        help="enable docker decorated tests",
    )
    parser.addoption(
        "--docker-build",
        action="store_true",
        dest="docker_build",
        default=False,
        help="enable docker_build decorated tests",
    )
    parser.addoption(
        "--upload-model",
        action="store_true",
        dest="upload_model",
        default=False,
        help="enable upload_model decorated tests",
    )
    parser.addoption(
        "--local-integration",
        action="store_true",
        dest="local_integration",
        default=False,
        help="enable local_integration decorated tests",
    )