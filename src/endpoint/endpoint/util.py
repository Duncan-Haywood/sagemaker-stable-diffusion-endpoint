import pickle
from typing import Dict, Tuple, Union
import boto3
from botocore.exceptions import ClientError
from . import config
import os
from .logger import get_logger

logger = get_logger(__name__)


def create_secret(secret_name: str, secret_string: str, description: str = ""):
    """Creates secret with error handling."""  # TODO switch to ssm
    sm = boto3.client("secretsmanager")
    response = None
    try:
        response = sm.create_secret(
            Name=secret_name,
            Description=description,
            SecretString=secret_string,
        )
        logger.info("secret upload %s", response["ReplicationStatus"][0]["Status"])
    except ClientError as error:
        if error.response["Error"]["Code"] == "ResourceExistsException":
            response = sm.put_secret_value(
                SecretId=secret_name, SecretString=secret_string
            )
            logger.info("secret exists, updated secret")
        else:
            logger.exception("")
            raise error
    except Exception as e:
        logger.exception("secret upload failed")
        raise e
    finally:
        return response


def get_secret(secret_name):
    """return secret value from secrets manager with secret_name as name of secret"""
    sm = boto3.client("secretsmanager")
    logger.info("secretsmanager client connected")
    try:
        response = sm.get_secret_value(SecretId=secret_name)
        secret = response["SecretString"]
        logger.info("secret retreived")
        return secret
    except Exception as e:
        logger.exception("secret not retrieved")
        raise e


def upload_file_to_s3(bucket_name: str, local_dir: str, key: str):
    """uploads file to s3"""
    try:
        s3 = boto3.resource("s3")
        bucket = s3.Bucket(bucket_name)
        with open(local_dir, "rb") as data:
            bucket.upload_fileobj(data, key)
        logger.info("file upload succeeded")
    except Exception as e:
        logger.exception("file upload failed")
        raise e


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


def file_exists(bucket_name: str, key: str) -> bool:
    """checks whether a file exists; only works with buckets with fewer than 1000 files"""
    s3 = boto3.client("s3")
    response = s3.list_objects_v2(Bucket=bucket_name)
    contents = response["Contents"]
    keys = [obj["Key"] for obj in contents]
    exists = key in keys
    return exists


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


def get_model_s3_key():
    config = get_config()
    return config["model_s3_key"]


def get_model_repository():
    config = get_config()
    model_repository = config["model_repository"]
    return model_repository


def get_huggingface_secret_name():
    config = get_config()
    secret_name = config["huggingface_token_secret_name"]
    return secret_name


def get_hugging_face_token():
    secret_name = get_huggingface_secret_name()
    hugging_face_token = get_secret(secret_name)
    return hugging_face_token


def get_endpoint_name():
    """gets endpoint name from ssm parameter store"""
    try:
        is_prod_bool = os.getenv("production", True)
        env = "production" if is_prod_bool else "test"
        param_store_name = f"endpoint_name/{env}"
        ssm = boto3.client("ssm")
        endpoint_name = ssm.get_parameter(Name=param_store_name)
        logger.info("get endpoint name succeeded")
        return endpoint_name
    except Exception as e:
        logger.exception("get endpoint name failed")
        raise e


def get_config():
    return config.config


def serialize_sagemaker_input(*args, **kwargs) -> bytes:
    # pickle supports PIL Image instances
    bytesobj = pickle.dumps((args, kwargs))
    return bytesobj


def deserialize_sagemaker_input(bytesobj: bytes) -> Tuple[tuple, dict]:
    kwargs = pickle.loads(bytesobj)
    return kwargs


def serialize_sagemaker_output(response: Union[dict, tuple]) -> bytes:
    bytesobj = pickle.dumps(response)
    return bytesobj


def deserialize_sagemaker_output(bytesobj: bytes) -> Union[dict, tuple]:
    predictions = pickle.loads(bytesobj)
    return predictions
