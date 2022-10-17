from endpoint import inference
import pytest
from PIL import Image
from io import BytesIO
from diffusers import StableDiffusionInpaintPipeline


@pytest.fixture
def image_size():
    return (512, 512)


@pytest.fixture
def data(image_size: tuple) -> Image:
    return Image.effect_noise(image_size, sigma=15)


@pytest.fixture
def model(model_dir) -> StableDiffusionInpaintPipeline:
    return inference.model_fn(model_dir)


@pytest.fixture
def model_dir() -> str:
    raise NotImplementedError


@pytest.fixture
def input_data(data: Image) -> BytesIO:
    image_bytes = BytesIO()
    file_type = "JPEG"
    data.save(image_bytes, format=file_type)
    return image_bytes


@pytest.fixture
def prediction() -> Image:
    raise NotImplementedError


@pytest.fixture
def accept() -> str:
    raise NotImplementedError


def test_predict_fn(data, model):
    inference.predict_fn(data, model, context=None)
    raise NotImplementedError


def test_model_fn(model_dir):
    inference.model_fn(model_dir, context=None)
    raise NotImplementedError


def test_input_fn(input_data):
    inference.input_fn(input_data)
    raise NotImplementedError


def test_output_fn(prediction, accept):
    inference.output_fn(prediction, accept)
    raise NotImplementedError


def test_model_fn_model_exists():
    raise NotImplementedError
