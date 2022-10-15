import yaml
import boto3
import logging
from botocore.exceptions import ClientError


def get_env():
    with open("./env.yaml", "rb") as file:
        env = yaml.safe_load(file)

    return env


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


def get_model_repository(env):
    model_repository = env["model_repository"]
    return model_repository


def get_huggingface_secret_name(env):
    secret_name = env["huggingface_token_secret_name"]
    return secret_name
