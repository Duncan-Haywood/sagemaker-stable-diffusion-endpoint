"""This inference.py script overwrites the default methods of the HuggingFaceHandlerService. (https://github.com/aws/sagemaker-huggingface-inference-toolkit/blob/main/src/sagemaker_huggingface_inference_toolkit/handler_service.py)  
The purpose here is to set up our HuggingFaceModel to use the diffusers module StableDiffusionInpaintPipeline for our predictions. See (https://github.com/huggingface/diffusers/blob/1070e1a38a41637400361a694966350fe790d5a4/src/diffusers/pipelines/stable_diffusion/pipeline_stable_diffusion_inpaint.py).

To use our inference.py we need to bundle it into a model.tar.gz archive with all our model-artifcacts. We then point to its s3 location with HuggingFaceModel - "model_data" __init__ paramater, and it will use the following insteaed of standard behavior. 

The custom module can override the following methods:

model_fn(model_dir) overrides the default method for loading a model. The return value model will be used in thepredict_fn for predictions.
model_dir is the the path to your unzipped model.tar.gz.
input_fn(input_data, content_type) overrides the default method for pre-processing. The return value data will be used in predict_fn for predictions. The inputs are:
input_data is the raw body of your request.
content_type is the content type from the request header.
predict_fn(processed_data, model) overrides the default method for predictions. The return value predictions will be used in output_fn.
model returned value from model_fn methond
processed_data returned value from input_fn method
output_fn(prediction, accept) overrides the default method for post-processing. The return value result will be the response to your request (e.g.JSON). The inputs are:
predictions is the result from predict_fn.
accept is the return accept type from the HTTP Request, e.g. application/json.

"""

from diffusers import StableDiffusionInpaintPipeline
import torch
from typing import Any, Tuple, Union, Dict
from diffusion_util import util
from logging import Logger

logger = Logger(__name__)


def download_model(local_dir: str):
    """Downloads model from s3 model bucket to local_dir"""
    # model_is_in_folder = NotImplemented
    # if model_is_in_folder:
    #     logger.info("model already downloaded")
    # else:
    config = util.get_config()
    bucket_name = util.get_model_bucket_name(config)
    key = util.get_model_s3_key(config)
    util.download_from_s3(bucket_name, local_dir, key)
    logger.info("model downloaded from s3")


def to_gpu(model: StableDiffusionInpaintPipeline) -> StableDiffusionInpaintPipeline:
    """Casts torch model to gpu if available."""
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model.to(device)
    return model


def model_fn(model_dir: str) -> StableDiffusionInpaintPipeline:
    """Load the saved model from the s3 bucket for the StableDiffuserInpaintPipeline (SDIP).

    Pipeline for text-guided image inpainting using Stable Diffusion. *This is an experimental feature*.
    This model inherits from [`DiffusionPipeline`]. Check the superclass documentation for the generic methods the
    library implements for all the pipelines (such as downloading or saving, running on a particular device, etc.)
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
    return predictions


def input_fn(input_data: bytes) -> Tuple[tuple, dict]:
    args_kwargs_tuple = util.deserialize_sagemaker_input(input_data)
    return args_kwargs_tuple


def output_fn(predictions: Union[dict, tuple], accept: str) -> bytes:
    """accept: can be ignored since the function from which this is called will handle it"""
    predicition_bytes = util.serialize_sagemaker_output(predictions)
    return predicition_bytes
