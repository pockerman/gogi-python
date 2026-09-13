"""This example illustrates the GuardrailsClient in gogi.
The client allows users to:

- Validate user-supplied input against a set of guardrail checks
- Filter/redact model output before it is returned to a user
- Check whether an action is allowed under a named policy
- Report a policy violation for auditing


"""


from loguru import logger
from rich import print as rich_print

from gogi.models.guardrails.requests.check_policy_request import CheckPolicyRequest
from gogi.models.guardrails.requests.filter_output_request import FilterOutputRequest
from gogi.models.guardrails.requests.report_violation_request import ReportViolationRequest
from gogi.models.guardrails.requests.validate_input_request import ValidateInputRequest

from gogi.gogi import Gogi

if __name__ == '__main__':

    # connect to the Gogi platform.
    # This will be the first step in any interaction with the platform, and will
    # give you access to all the available clients (indexes, documents, and queries).
    platform = Gogi(gateway_url="localhost:50051", logger=logger)

    # validate a piece of user input against a set of named checks
    validate_input_response = platform.guardrails.validate_input(
        request=ValidateInputRequest(
            content="What's the weather in London today?",
            checks=["pii", "prompt_injection"],
            context={"user_id": "123"},
        )
    )
    rich_print(f"Validate input response {validate_input_response}")

    # filter/redact model output before returning it to the user
    filter_output_response = platform.guardrails.filter_output(
        request=FilterOutputRequest(
            content="Sure, here is the info you asked for.",
            filters=["profanity", "pii"],
            context={"user_id": "123"},
        )
    )
    rich_print(f"Filter output response {filter_output_response}")

    # check whether an action is allowed under a named policy
    check_policy_response = platform.guardrails.check_policy(
        request=CheckPolicyRequest(
            policy_name="rate-limits",
            action="execute_tool",
            context={"user_id": "123"},
            arguments_json='{"tool_name": "get_weather"}',
        )
    )
    rich_print(f"Check policy response {check_policy_response}")

    # if the action was disallowed, report the violation for auditing
    if not check_policy_response.allowed:
        report_violation_response = platform.guardrails.report_violation(
            request=ReportViolationRequest(
                policy_name="rate-limits",
                action="execute_tool",
                severity="medium",
                context={"user_id": "123"},
                details=check_policy_response.denial_reason,
            )
        )
        rich_print(f"Report violation response {report_violation_response}")
