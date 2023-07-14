"""Run upload_huggingface_token.py before use -- a dependency."""
from diffusers import StableDiffusionInpaintPipeline
from . import util
import torch
from .logger import get_logger

logger = get_logger(__name__)


def load_model(hugging_face_token):
    """loads model from HuggingFace model hub into memory"""
    try:
        model = StableDiffusionInpaintPipeline.from_pretrained(
            "CompVis/stable-diffusion-v1-4", revision="fp16", torch_dtype=torch.float16
        )
        logger.info("model_download succeeded")
        return model
    except Exception as e:
        logger.exception("Failed model download")
        raise e


def save_model_local(model, local_dir):
    """saves model to local device"""
    try:
        model.save_pretrained(local_dir)
        logger.info("model save succeeded")
    except Exception as e:
        logger.exception("model save failed")
        raise e


def model_exists(bucket_name, folder_name) -> bool:
    """checks whether model already exists in bucket"""
    logger.info("checking if model exists")
    exists = util.folder_exists(bucket_name, folder_name)
    if exists:
        logger.info("model already exists")
    else:
        logger.info("model doesn't exist already")
    return exists


def main():
    """Download model from hugging face model hub and upload to s3 bucket."""
    # config
    local_dir = "./model"
    bucket_name = util.get_model_bucket_name()
    logger.info("bucket_name = %s" % bucket_name)
    folder = "model"
    hugging_face_token = util.get_hugging_face_token()
    # upload file
    if not model_exists(bucket_name, folder):
        model = load_model(hugging_face_token)
        save_model_local(model, local_dir)
        util.upload_folder_to_s3(bucket_name, local_dir, folder)
        logger.info("model uploaded to s3")


if __name__ == "__main__":
    main()
