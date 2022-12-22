import boto3
import os


def main():
    production = os.getenv("production")
    endpoint_name = os.getenv("endpoint_name")
    ssm = boto3.client("ssm")
    env = "production" if production=="True" else "test"
    param_name = f"endpoint_name/{env}"
    ssm.put_parameter(
        Name=param_name,
        Description="name of endpoint to be used when calling stable diffusion inpaint",
        Value=endpoint_name,
        Type="String",
        Overwrite=True,
    )
