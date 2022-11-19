"""Sagemaker Predictor() runs model_fn when initializing and on predictor.predict() -> it runs input_fn, predict_fn, output_fn in that order and returns that result."""
from diffusers import StableDiffusionInpaintPipeline
import torch
from typing import Any, Tuple, Union, Dict
from . import util
from .logger import get_logger

logger = get_logger(__name__)


def download_model(local_dir: str):
    """Downloads model from s3 model bucket to local_dir"""
    # model_is_in_folder = NotImplemented
    # if model_is_in_folder:
    #     logger.info("model already downloaded")
    # else:
    bucket_name = util.get_model_bucket_name()
    key = util.get_model_s3_key()
    util.download_from_s3(bucket_name, local_dir, key)
    logger.info("model downloaded from s3")


def to_gpu(model: StableDiffusionInpaintPipeline) -> StableDiffusionInpaintPipeline:
    """Casts torch model to gpu if available."""
    device_type = "cuda:0" if torch.cuda.is_available() else "cpu"
    device = torch.device(device_type)
    model.to(device)
    logger.info("model casted to %s" % device_type)
    return model


def model_fn(model_dir: str) -> StableDiffusionInpaintPipeline:
    """Load the saved model from the s3 bucket for the StableDiffuserInpaintPipeline (SDIP).

    Pipeline for text-guided image inpainting using Stable Diffusion.
    This model inherits from [`DiffusionPipeline`].

    Args:
        model_dir (str): local directory to which to save the model
    """
    download_model(model_dir)
    model = StableDiffusionInpaintPipeline.from_pretrained(
        model_dir,
        revision="fp16",
        torch_dtype=torch.float16,
    )
    logger.info("model loaded")
    model = to_gpu(model)

    return model


def predict_fn(
    args_kwargs_tuple: Tuple[Tuple[Any], Dict[str, Any]],
    model: StableDiffusionInpaintPipeline,
) -> Union[dict, tuple]:
    """
        This is what is called when sagemaker_endpoint.predict is run.
        runs predict on decoded_input_data deserialized in input_fn. Runs prediction on GPU if is available.

        Args:
            args_kwargs_tuple (tuple(tuple, dict)): deserialized (args, kwargs) as described below - returned by the input_fn. See `StableDiffusionInpaintPipeline` in `diffusers` for args and kwargs.
            model : Model returned by the `model_fn`.

    Returns:
        [`~pipelines.stable_diffusion.StableDiffusionPipelineOutput`] or `tuple`:
        [`~pipelines.stable_diffusion.StableDiffusionPipelineOutput`] if `return_dict` is True, otherwise a `tuple. (default true) type: ordered dict
        When returning a tuple, the first element is a list with the generated images, and the second element is a
        list of `bool`s denoting whether the corresponding generated image likely represents "not-safe-for-work"
        (nsfw) content, according to the `safety_checker`.
    """
    args = args_kwargs_tuple[0]
    kwargs = args_kwargs_tuple[1]
    predictions = model(*args, **kwargs)
    logger.info("predictions created")
    return predictions


def input_fn(input_data: bytes) -> Tuple[tuple, dict]:
    """Called on the data passed by sagemaker.Predictor().predict() and passes results to predict_fn"""
    args_kwargs_tuple = util.deserialize_sagemaker_input(input_data)
    logger.info("input deserialized")
    return args_kwargs_tuple


def output_fn(predictions: Union[dict, tuple], accept: str) -> bytes:
    """Called on output of predict_fn and passes result on to sagemaker.Predictor().predict() response.

    Args:
        accept: can be ignored since the function from which this is called will handle it"""
    predicition_bytes = util.serialize_sagemaker_output(predictions)
    logger.info("output serialized")
    return predicition_bytes
