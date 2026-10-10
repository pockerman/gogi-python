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
