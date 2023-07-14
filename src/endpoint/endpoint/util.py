import pickle
from typing import Tuple, Union
import boto3
import os
from logger import get_logger

logger = get_logger(__name__)


def download_from_s3(bucket_name: str, local_dir: str, key: str):
    """download file from s3"""
    try:
        s3 = boto3.resource("s3")
        bucket = s3.Bucket(bucket_name)
        with open(local_dir, "wb") as file:
            response = bucket.download_fileobj(key, file)
        logger.info("file download succeeded")
        return response
    except Exception as e:
        logger.exception("file download failed")


def get_model_bucket_name():
    try:
        model_bucket_name = os.getenv("model_bucket_name")
        if model_bucket_name is None:
            raise Exception("model_bucket_name in environment is not set")
        logger.info("succeeded")
        return model_bucket_name
    except Exception as e:
        logger.exception("failed")
        raise e


def deserialize_sagemaker_input(bytesobj: bytes) -> Tuple[tuple, dict]:
    kwargs = pickle.loads(bytesobj)
    return kwargs


def serialize_sagemaker_output(response: Union[dict, tuple]) -> bytes:
    bytesobj = pickle.dumps(response)
    return bytesobj
