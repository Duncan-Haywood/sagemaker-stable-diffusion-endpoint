import pytest
import subprocess
import sys
from logging import Logger
import time
import requests

logger = Logger(__name__)

docker_mark = pytest.mark.skipif("not config.getoption('docker_local')")
pytestmark = docker_mark


BASE_URL = "http://0.0.0.0:8080/"
PING_URL = BASE_URL + "ping"


@pytest.fixture
def docker_container():
    completed_process = subprocess.run(
        ["docker", "build", "--file", "Dockerfile.endpoint", "--tag", "server-test", "."], capture_output=True
    )
    logger.info(completed_process.stdout)
    completed_process.check_returncode()


@pytest.fixture(scope="module", autouse=True)
def container(docker_container):
    try:
        command = "docker run --name server-test -p 8080:8080"

        proc = subprocess.Popen(
            command.split(), stdout=sys.stdout, stderr=subprocess.STDOUT
        )

        attempts = 0
        while attempts < 10:
            time.sleep(3)
            try:
                requests.get(PING_URL)
                break
            except:
                attempts += 1
                pass
        yield proc.pid
    finally:
        subprocess.check_call("docker rm -f server-test".split())


def test_ping():
    res = requests.get(PING_URL)
    assert res.status_code == 200
