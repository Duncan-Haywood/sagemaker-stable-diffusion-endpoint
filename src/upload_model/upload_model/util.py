import boto3
from botocore.exceptions import ClientError
import os
from .logger import get_logger
import awscli 
import subprocess
logger = get_logger(__name__)


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
        logger.info("secret uploaded")
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


def upload_folder_to_s3(bucket_name: str,local_dir: str, folder: str):
    command = f"aws s3 cp {local_dir} {bucket_name}/{folder} --recursive"
    completed_process = subprocess.run(command.split(), capture_output=True)

def folder_exists(bucket_name, folder_name):
    s3 = boto3.client('s3')
    if not path.endswith('/'):
        path = path+'/' 
    resp = s3.list_objects(Bucket=bucket_name, Prefix=folder_name, Delimiter='/',MaxKeys=1)
    return 'Contents' in resp


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


def file_exists(bucket_name: str, key: str) -> bool:
    """checks whether a file exists; only works with buckets with fewer than 1000 files"""
    s3 = boto3.client("s3")
    response = s3.list_objects_v2(Bucket=bucket_name)
    logger.info("response %s" % response)
    try:
        contents = response["Contents"]
    except KeyError:
        logger.exception("no contents")
        exists = False
        return exists
    keys = [obj["Key"] for obj in contents]
    exists = key in keys
    return exists


def get_model_bucket_name():
    try:
        model_bucket_name = os.getenv("model_bucket_name")
        if model_bucket_name is None:
            raise Exception("model_bucket_name in environment is not set")
        logger.info("succeeded get model bucket")
        return model_bucket_name
    except Exception as e:
        logger.exception("failed get model bucket name")
        raise e


def get_hugging_face_token():
    hugging_face_token = get_secret("huggingface_api_token")
    return hugging_face_token
