import yaml
import boto3
import logging
from botocore.exceptions import ClientError


def get_config():
    with open("./config.yaml", "rb") as file:
        config = yaml.safe_load(file)

    return config


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


def get_model_repository(config):
    model_repository = config["model_repository"]
    return model_repository


def get_huggingface_secret_name(config):
    secret_name = config["huggingface_token_secret_name"]
    return secret_name


def upload_file_to_s3(bucket_name: str, local_dir: str, key: str):
    """uploads file to s3"""
    s3 = boto3.resource("s3")
    bucket = s3.Bucket(bucket_name)
    response = None
    with open(local_dir, "rb") as data:
        response = bucket.upload_fileobj(data, key)
    return response


def get_model_bucket_name(config):
    raise NotImplementedError


def get_model_s3_key(config):
    raise NotImplementedError
