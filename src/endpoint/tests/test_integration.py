import pytest
from PIL import Image
from endpoint import predict

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


@pytest.mark.skip(reason="Not implemented")
def test_predict_image(image):
    raise NotImplementedError


@pytest.mark.skip(reason="Not implemented")
def test_predict_prompt(prompt):
    raise NotImplementedError


@pytest.mark.skip(reason="Not implemented")
def test_multiple_thread_predicts(prompt, image):
    raise NotImplementedError
