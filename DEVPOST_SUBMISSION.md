# OpsPilot — Devpost Submission Copy

## Project Title

OpsPilot

## One-Line Tagline

An evidence-driven Strands agent that autonomously investigates AWS application incidents, performs policy-gated remediation, and verifies recovery.

## Track

Professional Agents

## Short Description

OpsPilot helps DevOps and cloud operations professionals reduce repetitive incident-response work. When a monitored application becomes unhealthy, it automatically collects the current service state and recent logs, reasons only from that evidence, performs an allowlisted recovery action, verifies the real application health endpoint, and produces a structured incident report.

## Inspiration / The Problem

Operations engineers repeatedly perform the same first-response steps when a service alert fires: confirm whether the service is running, inspect recent logs, decide whether a known remediation is safe, perform the action, and verify recovery.

Although each step may be straightforward, the complete process consumes attention, increases mean time to recovery, and interrupts engineers during routine incidents. A basic watchdog can restart a process, but it cannot interpret log evidence, explain what is known, distinguish a symptom from a root cause, or communicate uncertainty responsibly.

OpsPilot was created to automate this repetitive operational loop without giving a language model unrestricted control of infrastructure.

## Who It Is For

OpsPilot is designed for DevOps engineers, site reliability engineers, cloud operations teams, platform engineers, and small technical teams that manage services but may not have continuous dedicated incident-response coverage.

## What It Does

OpsPilot runs quietly in the background and responds when the demo application becomes unhealthy:

1. A systemd timer evaluates the `demo-api` service every minute.
2. It publishes a binary health metric to the `OpsPilot` CloudWatch namespace.
3. A CloudWatch alarm detects an unhealthy value.
4. EventBridge routes the alarm event to AWS Lambda.
5. Lambda uses AWS Systems Manager Run Command to launch the Strands agent on the designated EC2 instance.
6. The agent checks current service status and reads the most recent system logs.
7. It uses an Amazon Bedrock-hosted model to reason from the collected evidence.
8. A deterministic policy permits only an approved restart of `demo-api`; other service names are denied.
9. The agent verifies the internal `/health` endpoint and requires HTTP 200 before declaring success.
10. The next healthy metric returns the CloudWatch alarm to `OK`.

The final incident report includes the initial state, observed failure condition, relevant evidence, underlying root cause when supported, confidence, remediation action, verification result, and final status.

## How We Built It

The agent was implemented in Python using the Strands Agents SDK. Its reasoning model is accessed through Amazon Bedrock Mantle using the Strands OpenAI Responses model integration.

The agent has four narrow operational tools:

- `get_service_status` reads the current systemd state.
- `get_recent_logs` retrieves recent service logs.
- `restart_service` enforces the deterministic remediation allowlist.
- `verify_service_health` checks the internal HTTP health endpoint.

The surrounding AWS workflow uses Amazon EC2, CloudWatch custom metrics and alarms, EventBridge, Lambda, Systems Manager Run Command, IAM, and Amazon Bedrock. A minimal Python HTTP service provides a controlled workload for demonstrating failure and recovery.

The implementation deliberately keeps model reasoning separate from authorization. The model may assess evidence and select a tool, but the tool itself enforces which service and action are allowed.

## How OpsPilot Uses Strands Agents

Strands is the decision and tool-orchestration layer of OpsPilot, not a chat interface added to an automation script.

During an incident, the Strands agent determines the sequence of evidence-gathering and remediation tools. Its instructions require it to inspect current state and recent logs before acting, prioritize the latest evidence, distinguish the failure condition from the underlying cause, avoid unsupported conclusions, apply the approved recovery tool when appropriate, verify the outcome, and produce a complete incident report.

This creates a multi-step autonomous workflow in which reasoning is useful for interpreting operational evidence, while deterministic code retains control over infrastructure changes.

## Safety and Responsible Automation

OpsPilot is intentionally constrained:

- Only `demo-api` is approved for automatic remediation.
- Restart is the only approved action.
- Requests involving unknown services are denied.
- Evidence collection is required before remediation.
- A stopped service is treated as a failure condition, not automatically as its root cause.
- When logs do not explain why the service stopped, the root cause is explicitly reported as unknown.
- The incident is not marked resolved until the application responds with HTTP 200.
- Lambda can send SSM commands only to the designated EC2 instance using `AWS-RunShellScript`.
- CloudWatch publishing is restricted to the `OpsPilot` namespace.
- The application health port is not exposed publicly.
- Deployment-specific account IDs, instance IDs, IP addresses, keys, and credentials are excluded from the public repository.

## Challenges We Faced

The largest challenge was preventing the agent from treating an observed stopped state as a proven root cause. Early reports could describe “service stopped” as the cause, even though the logs only established the condition and did not explain the trigger.

We strengthened the agent instructions to prioritize recent evidence, distinguish symptoms from causes, communicate uncertainty, and avoid assigning high confidence without supporting logs. We repeatedly tested the complete workflow by stopping the service, allowing the alarm pipeline to invoke OpsPilot, and checking both the incident report and recovered health metric.

We also tightened the security design after the functional prototype worked. Public access to the application port was removed, SSH was restricted, Lambda's SSM permission was reduced to the designated instance and document, and configuration-specific identifiers were moved out of the public source code.

## Accomplishments That We Are Proud Of

- Built a fully autonomous event-driven incident loop rather than a prompt-only demonstration.
- Integrated Strands reasoning with real operational tools and AWS infrastructure.
- Demonstrated repeated end-to-end recovery from a controlled service outage.
- Preserved uncertainty instead of generating an unsupported root cause.
- Enforced a deterministic service-and-action allowlist.
- Verified recovery through the application endpoint rather than trusting the restart command alone.
- Returned the CloudWatch alarm from `ALARM` to `OK` after remediation.
- Published a sanitized, MIT-licensed repository with source code, setup instructions, IAM examples, tests, and an architecture diagram.

## Demonstrated Impact

In controlled end-to-end tests, OpsPilot detected and recovered the stopped demo service in approximately two to three minutes without manual investigation or restart. The engineer only initiated the test failure; detection, evidence collection, remediation, verification, and alarm recovery then occurred automatically.

The prototype demonstrates how teams can reduce repetitive first-response work and reserve human attention for incidents that require judgment beyond an approved runbook. It is particularly relevant for small operations teams and after-hours response, where even routine failures create interruption and delay.

## What We Learned

We learned that safe agentic operations require two different layers. The reasoning layer interprets evidence and decides which tool is appropriate. The deterministic layer defines what the tool is actually authorized to do.

We also learned that successful command execution is not the same as service recovery. A trustworthy incident agent must verify the application itself and communicate when the evidence is insufficient to identify the underlying cause.

Finally, we learned that a small, coherent architecture can demonstrate meaningful autonomy without adding unnecessary services. Each component in OpsPilot has a clear role in detection, routing, reasoning, controlled action, or verification.

## What's Next

Future versions could add:

- human approval for higher-risk actions;
- notifications containing the structured incident summary;
- additional explicitly allowlisted services and runbooks;
- persistent incident history and trend analysis;
- deployment through complete infrastructure as code;
- evaluation datasets for testing diagnostic accuracy;
- Amazon Bedrock AgentCore for managed agent deployment, observability, and production scaling.

These extensions would preserve the same principle: the agent may reason broadly, but infrastructure actions remain narrow, explicit, and verifiable.

## Technologies Used

- Strands Agents SDK
- Amazon Bedrock Mantle
- Amazon EC2
- Amazon CloudWatch
- Amazon EventBridge
- AWS Lambda
- AWS Systems Manager Run Command
- AWS IAM
- Python
- Bash
- systemd
- GitHub

## Links

- Public repository: https://github.com/Ratnadweep/opspilot
- Demo video: `[ADD VIDEO URL]`
- Optional live demo: Not provided; the application health endpoint remains private by design.
- Builder.aws article: `[ADD ARTICLE URL AFTER PUBLICATION]`
- AWS Builder ID: `[ENTER IN DEVPOST FORM]`

## Open-Source and Development Disclosure

OpsPilot was created during the hackathon submission period. It uses open-source libraries and standard AWS services identified in the repository. AI-assisted development tools were used to support planning, coding guidance, documentation, review, and troubleshooting. The implementation was tested against the deployed AWS workflow, and the submitted repository contains the project-specific source code and instructions.

