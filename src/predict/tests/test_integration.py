import pytest
from PIL import Image
from predict import main

integration = pytest.mark.skipif("not config.getoption('integration')")
pytestmark = integration


@pytest.fixture
def image():
    return Image.new(mode="RGB", size=(512, 512))


@pytest.fixture
def prompt():
    return "test"


def test_init_predictor():
    main.Predictor()


def test_predict_both(prompt, image):
    pred = main.Predictor()
    res = pred.predict(prompt, image)
    assert res is not None
