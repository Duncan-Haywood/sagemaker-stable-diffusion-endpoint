import pickle
from typing import Dict, Tuple, Union
import boto3
import logging
from botocore.exceptions import ClientError
from . import config


def create_secret(secret_name: str, secret_string: str, description: str = ""):
    """Creates secret with error handling."""
    sm = boto3.client("secretsmanager")
    response = None
    try:
        response = sm.create_secret(
            Name=secret_name,
            Description=description,
            SecretString=secret_string,
        )
        logging.info("secret upload %s", response["ReplicationStatus"][0]["Status"])
    except ClientError as error:
        if error.response["Error"]["Code"] == "ResourceExistsException":
            response = sm.put_secret_value(
                SecretId=secret_name, SecretString=secret_string
            )
            logging.info("secret exists, updated secret")
        else:
            logging.exception("")
            raise error
    except Exception as e:
        logging.exception("")
        raise e
    finally:
        return response


def get_secret(secret_name):
    """return secret value from secrets manager with secret_name as name of secret"""
    sm = boto3.client("secretsmanager")
    logging.info("ssm client connected")
    response = sm.get_secret_value(SecretId=secret_name)
    secret = response["SecretString"]
    return secret


def upload_file_to_s3(bucket_name: str, local_dir: str, key: str):
    """uploads file to s3"""
    s3 = boto3.resource("s3")
    bucket = s3.Bucket(bucket_name)
    response = None
    with open(local_dir, "rb") as data:
        response = bucket.upload_fileobj(data, key)
    return response


def download_from_s3(bucket_name: str, local_dir: str, key: str):
    """download file from s3"""
    s3 = boto3.resource("s3")
    bucket = s3.Bucket(bucket_name)
    with open(local_dir, "wb") as file:
        response = bucket.download_fileobj(key, file)


def get_model_bucket_name():
    config = get_config()
    raise NotImplementedError


def get_model_s3_key():
    config = get_config()
    raise NotImplementedError


def get_model_repository():
    config = get_config()
    model_repository = config["model_repository"]
    return model_repository


def get_huggingface_secret_name():
    config = get_config()
    secret_name = config["huggingface_token_secret_name"]
    return secret_name


def get_config():
    return config.config


def serialize_sagemaker_input(*args, **kwargs) -> bytes:
    # pickle supports PIL Image instances
    bytesobj = pickle.dumps(tuple(args, kwargs))
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
