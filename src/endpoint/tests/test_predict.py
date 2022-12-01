from endpoint import predict
import pytest
from PIL import Image
from moto import mock_sagemaker


pytestmark = pytest.mark.skip("Not implemented")


def test_init():
    pred = predict.Predictor()


@pytest.fixture
def predictor():
    with mock_sagemaker():
        return predict.Predictor()


@pytest.fixture
def image():
    size = (512, 512)
    mode = "RBG"
    return Image.new(mode, size)


@pytest.fixture
def prompt():
    return "test"


def test_predict(predictor, prompt, image):
    response = predictor.predict(prompt, image)
