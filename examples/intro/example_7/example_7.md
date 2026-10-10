# Guardrails

In this example we use the `GuardrailsClient` (`platform.guardrails`) to apply safety and policy checks around
a model: validate what goes into it, filter what comes out of it, check whether an action is allowed and
report violations for auditing.

| File            | What it does                                                                                     |
|-----------------|--------------------------------------------------------------------------------------------------|
| `example_7.py`  | Validates user input, filters model output, checks a tool execution against the `rate-limits` policy and reports a violation if it is denied |

## Prerequisites

- The Gogi platform running, with the gateway on `localhost:50051`

## Running the example

```bash
python examples/intro/example_7/example_7.py
```

## Walkthrough

### 1. Validate input

`platform.guardrails.validate_input(request=ValidateInputRequest(...))` runs a set of named checks on
user-supplied content before it reaches a model. The example runs the `pii` and `prompt_injection` checks.
The `context` (here the `user_id`) is passed to the checks.

### 2. Filter output

`filter_output(request=FilterOutputRequest(...))` filters or redacts model output before it is returned to
the user. The example applies the `profanity` and `pii` filters.

### 3. Check a policy

`check_policy(request=CheckPolicyRequest(...))` asks whether an action is allowed under a named policy. The
example checks whether user `123` may execute the `get_weather` tool under the `rate-limits` policy. The
response says whether the action is `allowed` and, if not, the `denial_reason`.

### 4. Report a violation

If the action is denied, `report_violation(request=ReportViolationRequest(...))` records the violation, with
its policy, action, severity, context and details, so it can be audited later.

## Driver code

The complete code of the example, `example_7.py`:

```python
"""This example illustrates the GuardrailsClient in gogi.
The client allows users to:

- Validate user-supplied input against a set of guardrail checks
- Filter/redact model output before it is returned to a user
- Check whether an action is allowed under a named policy
- Report a policy violation for auditing


"""

from loguru import logger
from rich import print as rich_print

from gogi.gogi import Gogi
from gogi.models.guardrails.requests.check_policy_request import CheckPolicyRequest
from gogi.models.guardrails.requests.filter_output_request import FilterOutputRequest
from gogi.models.guardrails.requests.report_violation_request import (
    ReportViolationRequest,
)
from gogi.models.guardrails.requests.validate_input_request import ValidateInputRequest

if __name__ == "__main__":
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
```
