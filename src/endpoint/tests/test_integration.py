import json
import subprocess
import sys
import time

import pytest
import requests

BASE_URL = "http://0.0.0.0:8080/"
PING_URL = BASE_URL + "ping"
INVOCATION_URL = BASE_URL + "models/{}/invoke"
MODELS_URL = BASE_URL + "models"
DELETE_MODEL_URL = BASE_URL + "models/{}"

pytestmark = pytest.mark.skipif("not config.getoption('integration')")


@pytest.fixture(scope="module", autouse=True)
def container():
    try:
        command = (
            "docker build --tag endpoint-test --file Dockerfile.endpoint . "
            "docker run --name endpoint -p 8080:8080 "
        )

        proc = subprocess.Popen(command.split(), stdout=sys.stdout, stderr=subprocess.STDOUT)

        attempts = 0
        while attempts < 10:
            time.sleep(3)
            try:
                requests.get(PING_URL)
                break
            except:  # noqa: E722
                attempts += 1
                pass
        yield proc.pid
    finally:
        subprocess.check_call("docker rm -f endpoint-test".split())


def make_list_model_request():
    response = requests.get(MODELS_URL)
    return response.status_code, json.loads(response.content.decode("utf-8"))


def make_load_model_request(content_type="application/json"):
    headers = {"Content-Type": content_type}
    response = requests.post(MODELS_URL, headers=headers)
    return response.status_code, json.loads(response.content.decode("utf-8"))


def make_unload_model_request(model_name):
    response = requests.delete(DELETE_MODEL_URL.format(model_name))
    return response.status_code, json.loads(response.content.decode("utf-8"))


def make_invocation_request(model_name, data, content_type="application/x-image"):
    headers = {"Content-Type": content_type}
    response = requests.post(INVOCATION_URL.format(model_name), data=data, headers=headers)
    return response.status_code, json.loads(response.content.decode("utf-8"))


def test_ping():
    res = requests.get(PING_URL)
    assert res.status_code == 200


def test_list_models_empty():
    code, models = make_list_model_request()
    assert code == 200
    assert models["models"] == []


def test_load_model():
    code1, content1 = make_load_model_request(data=json.dumps(data1))
    assert code1 == 200
    assert content1["status"] == "Workers scaled"

    code2, content2 = make_list_model_request()
    assert code2 == 200
    assert content2["models"] == [
        {"modelName": "resnet_152", "modelUrl": "/opt/ml/models/resnet_152/model"}
    ]

    data2 = {"model_name": "resnet_18", "url": "/opt/ml/models/resnet_18/model"}
    code3, content3 = make_load_model_request(data=json.dumps(data2))
    assert code3 == 200
    assert content3["status"] == "Workers scaled"

    code4, content4 = make_list_model_request()
    assert code4 == 200
    assert content4["models"] == [
        {"modelName": "resnet_152", "modelUrl": "/opt/ml/models/resnet_152/model"},
        {"modelName": "resnet_18", "modelUrl": "/opt/ml/models/resnet_18/model"},
    ]


def test_unload_models():
    code1, content1 = make_unload_model_request("resnet_152")
    assert code1 == 200
    assert content1["status"] == 'Model "resnet_152" unregistered'

    code2, content2 = make_list_model_request()
    assert code2 == 200
    assert content2["models"] == [
        {"modelName": "resnet_18", "modelUrl": "/opt/ml/models/resnet_18/model"}
    ]


def test_load_non_existing_model():
    data1 = {"model_name": "banana", "url": "/banana"}
    code1, content1 = make_load_model_request(data=json.dumps(data1))
    assert code1 == 404


def test_unload_non_existing_model():
    # resnet_152 is already unloaded
    code1, content1 = make_unload_model_request("resnet_152")
    assert code1 == 404


def test_load_model_multiple_times():
    # resnet_18 is already loaded
    data = {"model_name": "resnet_18", "url": "/opt/ml/models/resnet_18/model"}
    code3, content3 = make_load_model_request(data=json.dumps(data))
    assert code3 == 409