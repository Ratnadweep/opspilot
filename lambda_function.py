import json
import os
import boto3

REGION = os.getenv("AWS_REGION", "us-east-1")
INSTANCE_ID = os.environ["OPSPILOT_INSTANCE_ID"]

ssm = boto3.client("ssm", region_name=REGION)

def lambda_handler(event, context):
    print("OpsPilot received CloudWatch alarm event:")
    print(json.dumps(event))

    command = (
	f"OPSPILOT_INSTANCE_ID={INSTANCE_ID} "
        "/home/ec2-user/opspilot-venv/bin/python "
        "/home/ec2-user/agent.py "
        "> /tmp/opspilot-agent.log 2>&1"
    )

    response = ssm.send_command(
        InstanceIds=[INSTANCE_ID],
        DocumentName="AWS-RunShellScript",
        Parameters={
            "commands": [command]
        },
    )

    command_id = response["Command"]["CommandId"]

    print(f"OpsPilot agent launched through SSM: {command_id}")

    return {
        "statusCode": 200,
        "commandId": command_id
    }