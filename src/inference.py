from diffusers import StableDiffusionInpaintPipeline
import torch


def model_fn(model_dir, **kwargs):
    pipe = StableDiffusionInpaintPipeline.from_pretrained(model_dir, kwargs)
    pipe.to("cuda")
    return pipe


def predict_fn(prompt, pipe, **kwargs):
    with torch.autocast("cuda"):
        result = pipe(prompt)
    images = result[0]

    return images
