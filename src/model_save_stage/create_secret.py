from venv import create
import typer
import yaml
import boto3
import logging
from botocore.exceptions import ClientError


def create_secret(secret_name: str, token: str):
    """creates hugging face token for use in model download and upload.
    Args:
        token: the Huggingface model hub api token."""
    sm = boto3.client("secretsmanager")
    try:
        response = sm.create_secret(
            Name=secret_name,
            Description="Huggingfce api token for model hub",
            SecretString=token,
        )
        logging.info("secret upload %s", response["ReplicationStatus"][0]["Status"])
    except ClientError as error:
        if error.response["Error"]["Code"] == "ResourceExistsException":
            response = sm.put_secret_value(SecretId=secret_name, SecretString=token)
            logging.info("secret exists, updated secret")

        else:
            logging.exception("")
            raise error

    finally:
        return response


def get_env():
    with open("./env.yaml", "rb") as file:
        env = yaml.safe_load(file)

    return env


def get_token_secret_name(env):
    secret_name = env["huggingface_token_secret_name"]
    return secret_name


def main():
    token = typer.prompt("hugging face api token:")
    env = get_env()
    secret_name = get_token_secret_name(env)
    create_secret(secret_name, token)


if __name__ == "__main__":
    typer.run(main)
