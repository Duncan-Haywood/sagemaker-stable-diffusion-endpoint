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
    raise NotImplementedError
