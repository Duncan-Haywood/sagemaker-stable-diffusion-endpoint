# need to set function_name in environment to use
import boto3
import logging
import os


def main():
    function_name = os.getenv("function_name")
    client = boto3.client("lambda")
    response = client.invoke(
        FunctionName=function_name, InvocationType="RequestResponse"
    )
    logging.info("model upload request response = %s" % response["StatusCode"])
    assert response["StatusCode"] == "200"  # succeeded


if __name__ == "__main__":
    main
