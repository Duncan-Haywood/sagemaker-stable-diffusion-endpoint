import pytest
import subprocess

docker_mark = pytest.mark.skipif("not config.getoption('docker_build')")
pytestmark = docker_mark
from logging import Logger

logger = Logger(__name__)


def test_endpoint_docker():
    completed_process = subprocess.run(
        ["docker", "build", "--file", "Dockerfile.endpoint", "."], capture_output=True
    )
    logger.info(completed_process.stdout)
    completed_process.check_returncode()


def test_model_upload_docker():
    completed_process = subprocess.run(
        ["docker", "build", "--file", "Dockerfile.model_upload", "."],
        capture_output=True,
    )
    logger.info(completed_process.stdout)
    completed_process.check_returncode()
