import os
import json
import logging
import time
from typing import Dict, List
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

logger.critical("Function startup")

AWS_REGION = os.environ["AWS_REGION"]

ssm_client = boto3.client("ssm", region_name=AWS_REGION)
cfn_client = boto3.client("cloudformation", region_name=AWS_REGION)


def handler(event, _):
    logger.info("Event: %s", json.dumps(event))

    # Get TTL parameters
    ttl_params = ssm_client.get_parameters_by_path(Path="/aw3/cfn/ttl/")

    # Check for expired TTL values
    for param in ttl_params["Parameters"]:
        stack_name = param["Name"].split("/")[-1]
        value = int(param["Value"])
        if value < time.time():
            # TTL expired, delete stack
            try:
                cfn_client.describe_stacks(StackName=stack_name)
                cfn_client.delete_stack(StackName=stack_name)
            except ClientError as e:
                if e.response["Error"]["Code"] == "ValidationError":
                    # Stack already deleted
                    ssm_client.delete_parameter(Name=param["Name"])
                else:
                    raise e

    return {"message": "success"}
