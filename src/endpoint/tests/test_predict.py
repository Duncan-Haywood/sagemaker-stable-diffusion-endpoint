from endpoint import predict
import pytest
from PIL import Image
from moto import mock_sagemaker

integration = pytest.mark.skipif("not config.getoption('integration')")


def test_init():
    with mock_sagemaker():
        pred = predict.Predictor()


@pytest.fixture
def predictor():
    with mock_sagemaker():
        return predict.Predictor()


@pytest.fixture
def init_image():
    size = (512, 512)
    mode = "RBG"
    return Image.new(mode, size)


@pytest.fixture
def prompt():
    return "test"


@integration
def test_predict(predictor, prompt, init_image):
    response = predictor.predict(prompt, init_image)
    assert type(response) == dict or type(response) == tuple
    if type(response) == tuple:
        images = response[0]
        sfw = response[1]
        assert type(images) == list
        assert type(sfw) == list
        assert type(images[0]) is not None  # not empty
        assert type(images[0]) == Image.Image
        assert type(sfw) == bool
