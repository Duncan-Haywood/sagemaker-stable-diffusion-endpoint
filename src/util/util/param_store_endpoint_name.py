import boto3
import os
from .logger import get_logger

logger = get_logger(__name__)


def main():
    env = os.getenv("env")
    logger.info("env = %s" % env)
    endpoint_name = os.getenv("endpoint_name")
    logger.info("endpoint name = %s" % endpoint_name)
    ssm = boto3.client("ssm")
    param_name = f"/endpoint_name/{env}"
    logger.info("parameter name = %s" % param_name)
    try:
        ssm.put_parameter(
            Name=param_name,
            Description="name of endpoint to be used when calling stable diffusion inpaint",
            Value=endpoint_name,
            Type="String",
            Overwrite=True,
        )
        logger.info("endpoint name uploaded")
    except Exception as e:
        logger.exception("upload failed")
        raise e


if __name__ == "__main__":
    main()
