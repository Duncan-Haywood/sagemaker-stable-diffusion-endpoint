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
from logging import Logger


def model_fn(model_dir, **kwargs):
    """This overwrites the load() function in a sagemaker HuggingFaceHandlerService. It tells how to 
    """
    model = StableDiffusionInpaintPipeline.from_pretrained(model_dir, kwargs)
    try:
        model.to("cuda")
    except:
        Logger(__name__).warning("model.to('cuda') didn't work'")
    finally:
        return model


def predict_fn(prompt, model, **kwargs):
    """
        This overwrites the predict handler. It is responsible for model predictions. Calls the `__call__` method of the provided `modelline`
        on decoded_input_data deserialized in input_fn. Runs prediction on GPU if is available.
        Args:
            prompt (dict): deserialized decoded_input_data returned by the input_fn
            model : Model returned by the `load` method or if it is a custom module `model_fn`.
        Returns:
            obj (dict): prediction result.

    Function invoked when calling the pipeline for generation.
    Args + kwargs:
        prompt (`str` or `List[str]`):
            The prompt or prompts to guide the image generation.
        init_image (`torch.FloatTensor` or `PIL.Image.Image`):
            `Image`, or tensor representing an image batch, that will be used as the starting point for the
            process. This is the image whose masked region will be inpainted.
        mask_image (`torch.FloatTensor` or `PIL.Image.Image`):
            `Image`, or tensor representing an image batch, to mask `init_image`. White pixels in the mask will be
            replaced by noise and therefore repainted, while black pixels will be preserved. If `mask_image` is a
            PIL image, it will be converted to a single channel (luminance) before use. If it's a tensor, it should
            contain one color channel (L) instead of 3, so the expected shape would be `(B, H, W, 1)`.
        strength (`float`, *optional*, defaults to 0.8):
            Conceptually, indicates how much to inpaint the masked area. Must be between 0 and 1. When `strength`
            is 1, the denoising process will be run on the masked area for the full number of iterations specified
            in `num_inference_steps`. `init_image` will be used as a reference for the masked area, adding more
            noise to that region the larger the `strength`. If `strength` is 0, no inpainting will occur.
        num_inference_steps (`int`, *optional*, defaults to 50):
            The reference number of denoising steps. More denoising steps usually lead to a higher quality image at
            the expense of slower inference. This parameter will be modulated by `strength`, as explained above.
        guidance_scale (`float`, *optional*, defaults to 7.5):
            Guidance scale as defined in [Classifier-Free Diffusion Guidance](https://arxiv.org/abs/2207.12598).
            `guidance_scale` is defined as `w` of equation 2. of [Imagen
            Paper](https://arxiv.org/pdf/2205.11487.pdf). Guidance scale is enabled by setting `guidance_scale >
            1`. Higher guidance scale encourages to generate images that are closely linked to the text `prompt`,
            usually at the expense of lower image quality.
        eta (`float`, *optional*, defaults to 0.0):
            Corresponds to parameter eta (η) in the DDIM paper: https://arxiv.org/abs/2010.02502. Only applies to
            [`schedulers.DDIMScheduler`], will be ignored for others.
        generator (`torch.Generator`, *optional*):
            A [torch generator](https://pytorch.org/docs/stable/generated/torch.Generator.html) to make generation
            deterministic.
        output_type (`str`, *optional*, defaults to `"pil"`):
            The output format of the generate image. Choose between
            [PIL](https://pillow.readthedocs.io/en/stable/): `PIL.Image.Image` or `np.array`.
        return_dict (`bool`, *optional*, defaults to `True`):
            Whether or not to return a [`~pipelines.stable_diffusion.StableDiffusionPipelineOutput`] instead of a
            plain tuple.
        callback (`Callable`, *optional*):
            A function that will be called every `callback_steps` steps during inference. The function will be
            called with the following arguments: `callback(step: int, timestep: int, latents: torch.FloatTensor)`.
        callback_steps (`int`, *optional*, defaults to 1):
            The frequency at which the `callback` function will be called. If not specified, the callback will be
            called at every step.
    Returns:
        [`~pipelines.stable_diffusion.StableDiffusionPipelineOutput`] or `tuple`:
        [`~pipelines.stable_diffusion.StableDiffusionPipelineOutput`] if `return_dict` is True, otherwise a `tuple.
        When returning a tuple, the first element is a list with the generated images, and the second element is a
        list of `bool`s denoting whether the corresponding generated image likely represents "not-safe-for-work"
        (nsfw) content, according to the `safety_checker`.
    """
    with torch.autocast("cuda"):
        prediction = model(prompt, kwargs)
    safe_for_work_images = get_safe_for_work_images(prediction)

    return safe_for_work_images


def get_safe_for_work_images(prediction):
    """Filters images on whether they are safe for work or not and returns only ones that are SFW."""
    safe_for_work_images = [
        prediction[0][i] for i in range(len(prediction[1])) if not prediction[1][i]
    ]
    return safe_for_work_images
