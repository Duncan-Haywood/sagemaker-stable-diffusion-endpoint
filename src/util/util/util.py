from botocore import ClientError
import boto3
from .logger import get_logger

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
