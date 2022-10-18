"""Run upload_huggingface_token.py before use -- a dependency."""
from diffusers import StableDiffusionInpaintPipeline
import logging
from diffusion_util import util
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
        logging.exception("Failed model download")
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


def get_config() -> dict:
    config = util.get_config()
    huggingface_secret_name = util.get_huggingface_secret_name(config)

    return dict(
        model_id=util.get_model_repository(config),
        local_dir="./model",
        bucket_name=util.get_model_bucket_name(config),
        key=util.get_model_s3_key(config),
        hugging_face_token=util.get_secret(huggingface_secret_name),
    )


def main():
    d = get_config()
    model = load_model(d.model_id, d.hugging_face_token)
    save_model_local(model, d.local_dir)
    util.upload_file_to_s3(d.bucket_name, d.local_dir, d.key)


def lambda_handler(event, context):
    main()


if __name__ == "__main__":
    main()
