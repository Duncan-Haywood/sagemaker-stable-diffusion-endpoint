import pickle
from typing import Dict, Tuple, Union
import boto3
from botocore.exceptions import ClientError
import os
from .logger import get_logger

logger = get_logger(__name__)


def get_endpoint_name():
    """gets endpoint name from ssm parameter store"""
    try:
        is_prod_bool = os.getenv("production", "True")
        env = "production" if is_prod_bool == "True" else "test"
        param_store_name = f"/endpoint_name/{env}"
        ssm = boto3.client("ssm")
        response = ssm.get_parameter(Name=param_store_name)
        logger.info("get endpoint name succeeded")
        logger.info("response: %s " % str(response))
        endpoint_name = response["Parameter"]["Value"]
        logger.info("endpoint name: %s" % endpoint_name)
        return endpoint_name
    except Exception as e:
        logger.exception("get endpoint name failed")
        raise e


def serialize_sagemaker_input(*args, **kwargs) -> bytes:
    # pickle supports PIL Image instances
    bytesobj = pickle.dumps((args, kwargs))
    return bytesobj


def deserialize_sagemaker_output(bytesobj: bytes) -> Union[dict, tuple]:
    predictions = pickle.loads(bytesobj)
    return predictions
