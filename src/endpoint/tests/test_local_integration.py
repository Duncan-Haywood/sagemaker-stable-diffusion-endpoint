from endpoint import upload_model
from endpoint import inference
import pytest



def test_model_exists():
    """should be run after model has already been truly uploaded"""
    config = upload_model.get_config()
    bucket_name = config.bucket_name
    key = config.key
    assert upload_model.model_exists(bucket_name, key)

class TestInference:
    def test_model_download(tmp_path):
        local_dir=tmp_path
        inference.download_model(local_dir)

    def test_model_fn(model_dir):
        pass


    def test_to_gpu(model):
        raise NotImplementedError


    def test_predict_fn(data, model):
        inference.predict_fn(data, model)
        raise NotImplementedError


    def test_input_fn(input_data: bytes):
        input = inference.input_fn(input_data)
        args = input[0]
        kwargs = input[1]

        raise NotImplementedError


    def test_output_fn(prediction, accept):
        inference.output_fn(prediction, accept)
        raise NotImplementedError

class TestServer:
    pass