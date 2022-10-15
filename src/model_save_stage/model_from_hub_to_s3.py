"""Run upload_huggingface_token.py before use -- a dependency."""
from diffusers import StableDiffusionInpaintPipeline
import logging
import boto3
from . import util
import torch


def load_model(model_id, hugging_face_token):
    """loads model from HuggingFace into memory"""
    model = None
    try:
        model = StableDiffusionInpaintPipeline.from_pretrained(
            model_id,
            use_auth_token=hugging_face_token,
            revision="fp16",
            torch_dtype=torch.float16,
        )
        logging.info("model_download succeeded")
    except Exception as e:
        logging.exception("failed model download")
        raise e
    finally:
        return model


def save_model_local(model, local_dir):
    """saves model to local device"""
    try:
        model.save_pretrained(local_dir)
        logging.info("model save succeeded")
    except Exception as e:
        logging.exception("model save failed")
        raise e


def upload_model_to_s3(local_dir):
    s3 = boto3.resource("s3")
    bucket = s3.Bucket()


def main():
    env = util.get_env()
    model_id = util.get_model_repository(env)
    local_dir = "./model"
    huggingface_secret_name = util.get_huggingface_secret_name(env)
    hugging_face_token = util.get_secret(huggingface_secret_name)
    model = load_model(model_id, hugging_face_token)
    save_model_local(model, local_dir)
    upload_model_to_s3(local_dir)


if __name__ == "__main__":
    main()
