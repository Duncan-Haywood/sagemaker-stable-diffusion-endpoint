"""Run upload_huggingface_token.py before use -- a dependency."""
from diffusers import StableDiffusionInpaintPipeline
from . import util
import torch
from .logger import get_logger

logger = get_logger(__name__)


def load_model(model_id, hugging_face_token):
    """loads model from HuggingFace model hub into memory"""
    try:
        model = StableDiffusionInpaintPipeline.from_pretrained(
            model_id,
            use_auth_token=hugging_face_token,
            revision="fp16",
            torch_dtype=torch.float16,
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


def get_config() -> dict:
    return dict(
        model_id=util.get_model_repository(),
        local_dir="./model",
        bucket_name=util.get_model_bucket_name(),
        key=util.get_model_s3_key(),
        hugging_face_token=util.get_hugging_face_token(),
    )


def model_exists(bucket_name, key) -> bool:
    """checks whether model already exists in bucket"""
    exists = util.file_exists(bucket_name, key)
    if exists:
        logger.info("model already exists")
    else:
        logger.info("model doesn't exist already")
    return exists


def main():
    """Download model from hugging face model hub and upload to s3 bucket."""
    d = get_config()
    if not model_exists(d.bucket_name, d.key):
        model = load_model(d.model_id, d.hugging_face_token)
        save_model_local(model, d.local_dir)
        util.upload_file_to_s3(d.bucket_name, d.local_dir, d.key)
        logger.info("model uploaded to s3")


def lambda_handler(event, context):
    main()


if __name__ == "__main__":
    main()
