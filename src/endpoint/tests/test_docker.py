import pytest
import subprocess

from logging import Logger

logger = Logger(__name__)

docker_mark = pytest.mark.skipif("not config.getoption('docker')")
pytestmark = docker_mark


@pytest.mark.skip(reason="Not implemented")
def test_ping():
    raise NotImplementedError
