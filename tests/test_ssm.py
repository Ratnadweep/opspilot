import os
import time
import boto3

REGION = os.getenv("AWS_REGION", "us-east-1")
INSTANCE_ID = os.environ["OPSPILOT_INSTANCE_ID"]

ssm = boto3.client("ssm", region_name=REGION)


def run_command(command: str) -> dict:
    response = ssm.send_command(
        InstanceIds=[INSTANCE_ID],
        DocumentName="AWS-RunShellScript",
        Parameters={
            "commands": [command]
        },
    )

    command_id = response["Command"]["CommandId"]

    for _ in range(15):
        time.sleep(1)

        result = ssm.get_command_invocation(
            CommandId=command_id,
            InstanceId=INSTANCE_ID,
        )

        if result["Status"] not in ["Pending", "InProgress", "Delayed"]:
            return result

    raise TimeoutError("SSM command did not finish in time")


result = run_command("systemctl is-active demo-api")

print("SSM status:", result["Status"])
print("Response code:", result["ResponseCode"])
print("Service status:", result["StandardOutputContent"].strip())
print("Error:", result["StandardErrorContent"].strip())