from endpoint import inference
import pytest
from PIL import Image as ImageModule
from PIL.Image import Image
from diffusers import StableDiffusionInpaintPipeline


@pytest.fixture
def image_size():
    return (512, 512)


@pytest.fixture
def data(image_size: tuple) -> Image:
    return ImageModule.new("RGB", image_size)


@pytest.fixture
def model(model_dir) -> StableDiffusionInpaintPipeline:
    return inference.model_fn(model_dir)


@pytest.fixture
def model_dir() -> str:
    raise NotImplementedError


@pytest.fixture
def input_data(data: Image) -> bytes:
    raise NotImplementedError


@pytest.fixture
def prediction() -> Image:
    raise NotImplementedError


@pytest.fixture
def accept() -> str:
    raise NotImplementedError

@pytest.mark.skip(reason="Not implemented")
def test_download_model(model_dir):
    raise NotImplementedError

@pytest.mark.skip(reason="Not implemented")
def test_to_gpu(model):
    raise NotImplementedError

@pytest.mark.skip(reason="Not implemented")
def test_predict_fn(data, model):
    inference.predict_fn(data, model)
    raise NotImplementedError

@pytest.mark.skip(reason="Not implemented")
def test_model_fn(model_dir):
    inference.model_fn(model_dir)
    raise NotImplementedError

@pytest.mark.skip(reason="Not implemented")
def test_input_fn(input_data: bytes):
    input = inference.input_fn(input_data)
    args = input[0]
    kwargs = input[1]

    raise NotImplementedError

@pytest.mark.skip(reason="Not implemented")
def test_output_fn(prediction, accept):
    inference.output_fn(prediction, accept)
    raise NotImplementedError
