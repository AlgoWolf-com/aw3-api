import json
import logging
import boto3
import cfnresponse
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

logger.critical("Function startup")


r53domains_client = boto3.client("route53domains", region_name="us-east-1")


def handler(event, ctx):
    logger.info("Event: %s", json.dumps(event))

    result = cfnresponse.FAILED
    try:
        if event["RequestType"] in ("Create", "Update"):
            domain_name = event["ResourceProperties"]["DomainName"]
            nameservers = [
                {"Name": ns} for ns in event["ResourceProperties"]["NameServers"]
            ]
            r53domains_client.update_domain_nameservers(
                DomainName=domain_name, Nameservers=nameservers
            )
            result = cfnresponse.SUCCESS
    except ClientError as err:
        logger.error("Error: %s", err)
        result = cfnresponse.FAILED

    cfnresponse.send(event, ctx, result, {})
