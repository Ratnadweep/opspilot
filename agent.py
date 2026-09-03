import os
import time
import boto3

from strands import Agent, tool
from strands.models.openai_responses import OpenAIResponsesModel


REGION = os.getenv("AWS_REGION", "us-east-1")
INSTANCE_ID = os.environ["OPSPILOT_INSTANCE_ID"]

ssm = boto3.client("ssm", region_name=REGION)


def run_ssm_command(command: str) -> dict:
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


@tool
def get_service_status() -> str:
    """Return the current status of the demo application service."""

    result = run_ssm_command(
        "systemctl is-active demo-api"
    )

    status = result["StandardOutputContent"].strip()

    if status:
        return f"Service status: {status}"

    return "Service status: unknown"


@tool
def verify_service_health(service_name: str) -> str:
    """Verify whether the demo service is healthy after remediation."""

    if service_name != "demo-api":
        return f"Verification unavailable for {service_name}"

    result = run_ssm_command(
        "curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health"
    )

    http_code = result["StandardOutputContent"].strip()

    if result["ResponseCode"] == 0 and http_code == "200":
        return "Verification result: demo-api is healthy, HTTP 200"

    error = result["StandardErrorContent"].strip()

    return (
        f"Verification result: demo-api is unhealthy. "
        f"HTTP status: {http_code or 'unknown'}. "
        f"Error: {error}"
    )


@tool
def get_recent_logs() -> str:
    """Return recent logs relevant to the current demo application incident."""

    result = run_ssm_command(
        "journalctl -u demo-api --since '30 minutes ago' -n 50 --no-pager"
    )

    logs = result["StandardOutputContent"].strip()

    if logs:
        return f"Recent demo-api logs from the last 30 minutes:\n{logs}"

    return "No demo-api logs found in the last 30 minutes."


@tool
def restart_service(service_name: str) -> str:
    """Restart an approved service only when remediation policy allows it."""

    remediation_policy = {
        "demo-api": {
            "action": "restart",
            "enabled": True,
        }
    }

    policy = remediation_policy.get(service_name)

    if policy is None:
        return (
            f"DENIED: {service_name} is not an approved service "
            "for automated remediation."
        )

    if not policy["enabled"]:
        return (
            f"DENIED: automated remediation is disabled "
            f"for {service_name}."
        )

    if policy["action"] != "restart":
        return (
            f"DENIED: restart is not an approved action "
            f"for {service_name}."
        )

    result = run_ssm_command(
        f"sudo systemctl restart {service_name}"
    )

    if result["ResponseCode"] == 0:
        return (
            f"SUCCESS: policy approved restart of "
            f"{service_name}; command completed."
        )

    error = result["StandardErrorContent"].strip()

    return (
        f"FAILED: approved restart of {service_name} failed. "
        f"Error: {error}"
    )


model = OpenAIResponsesModel(
    model_id="openai.gpt-oss-120b",
    bedrock_mantle_config={
        "region": REGION
    },
)

agent = Agent(
    model=model,
    tools=[
        get_service_status,
        get_recent_logs,
        restart_service,
        verify_service_health,
    ],
)

if __name__ == "__main__":
    agent(
    "Investigate the unhealthy demo application. "
    "Use get_service_status and get_recent_logs before taking remediation action. "
    "Base every conclusion strictly on tool evidence. "
    "Prioritize the most recent log entries when analyzing the current incident. "
    "Do not treat an older historical error as the current root cause unless recent "
    "evidence directly connects it to the current outage. "
    "If the exact root cause cannot be established, explicitly report that the root "
    "cause is unknown rather than guessing. "
    "Always distinguish the observed failure condition from the underlying root cause. "
    "A service being stopped, inactive, unhealthy, or unavailable is a failure condition, "
    "not by itself an underlying root cause. "
    "If the evidence shows that demo-api stopped but does not explain why it stopped, "
    "report the failure condition as 'service stopped/inactive' and the underlying root "
    "cause as 'unknown'. "
    "Never assign high root-cause confidence merely because the stopped state is confirmed. "
    "If demo-api is confirmed inactive, restart it using the approved remediation tool. "
    "After remediation, verify actual service health using the verification tool. "
    "Do not declare the incident resolved unless verification succeeds. "
    "Report: initial state, failure condition, relevant evidence, underlying root cause, "
    "root-cause confidence, remediation action, verification result, and final incident status."
)