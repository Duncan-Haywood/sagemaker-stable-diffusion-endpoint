import pytest
from PIL import Image
from endpoint import predict, upload_model, inference

integration = pytest.mark.skipif("not config.getoption('integration')")
pytestmark = integration


@pytest.fixture
def image():
    size = (512, 512)
    mode = "RBG"
    return Image.new(mode, size)


@pytest.fixture
def prompt():
    return "test"


def test_init_predictor():
    pred = predict.Predictor()


def test_predict_both(prompt, image):
    pred = predict.Predictor()
    res = pred.predict(prompt, image)
    assert res is not None

def test_model_exists():
    config = upload_model.get_config()
    bucket_name = config.bucket_name
    key = config.key
    assert upload_model.model_exists(bucket_name, key)

def test_model_download(tmp_path):
    local_dir=tmp_path
    inference.download_model(local_dir)

def test_model_fn(model_dir):
    