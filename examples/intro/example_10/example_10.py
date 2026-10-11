"""This example illustrates the ObservabilityClient in gogi, with a recipe assistant that
suggests dishes from what is in the fridge:

- Traces a request: the application's own spans, and the spans the platform's services
  record for the calls made inside the trace, nest into one trace
- Records structured log events and metrics, and scores the response
- Finds the trace again, with its generations and scores, and searches traces by quality
- Reports the cost of model calls, sets a budget, and checks the health of the services

See example_10.md for a discussion of the example.
"""

import time
import uuid

import grpc
from loguru import logger
from rich import print as rich_print
from rich.rule import Rule

from gogi.gogi import Gogi
from gogi.models import LLMMessage, LLMRunRequest, LLMRunRequestConfig
from gogi.models.observability import BudgetAlert

WORKFLOW = "example-10-recipes"
SESSION = f"example-10-{uuid.uuid4().hex[:8]}"
FRIDGE = ["leeks", "eggs", "feta", "spinach"]


def now_ms() -> int:
    return int(time.time() * 1000)


def suggest_recipe(platform: Gogi) -> str:
    """Handles a request inside a trace; returns the trace id"""
    rich_print(Rule("Tracing a request"))
    obs = platform.observability

    question = f"What can I cook with {', '.join(FRIDGE)}?"
    with obs.trace(
        "recipes.suggest", session_id=SESSION, user_id="cook-1", workflow_id=WORKFLOW, input=question, team="kitchen"
    ) as root:
        # the application's own work gets spans of its own
        with obs.span("recipes.check_pantry", items=len(FRIDGE)):
            obs.log("pantry_checked", f"{len(FRIDGE)} items available", attributes={"source": "fridge-sensor"})

        # calls to the platform inside the trace carry it: the gateway and the model service
        # record their spans, and the model service a generation, in this trace
        answer = "A leek, spinach and feta frittata."
        try:
            response = platform.llm_clients.run(
                LLMRunRequest(
                    config=LLMRunRequestConfig(provider="openai", model="gpt-4o-mini", max_tokens=200),
                    messages=[LLMMessage(role="user", content=question)],
                )
            )
            answer = response.content
        except (grpc.RpcError, ValueError) as e:
            rich_print(f"[yellow]The model call failed ({e}); continuing with a canned answer[/yellow]")

        with obs.span("recipes.rank") as rank:
            rank.set_attribute("candidates", 3)
            obs.histogram("recipes.ranking_ms", 12.5, labels={"workflow_id": WORKFLOW})
        obs.counter("recipes.suggestions_total", labels={"workflow_id": WORKFLOW})
        root.set_output(answer)

    rich_print(f"Trace {root.trace_id}: {answer[:80]}")
    return root.trace_id


def score_and_query(platform: Gogi, trace_id: str) -> None:
    rich_print(Rule("Scores and queries"))
    obs = platform.observability

    # quality signals from code, a reviewer and the user
    obs.score(trace_id, "uses_fridge_items", True, "AUTOMATED")
    obs.score(trace_id, "tastiness", 0.4, "HUMAN", comment="too plain")
    obs.score(trace_id, "thumbs_up", False, "USER_FEEDBACK")

    # telemetry is sent in batches; the platform's services send theirs every few seconds
    obs.flush()
    time.sleep(6)

    trace = obs.get_trace(trace_id)
    rich_print(
        f"{trace.span_count} spans, {trace.total_tokens} tokens, ${trace.total_cost_usd:.6f}, "
        f"{trace.total_duration_ms:.0f} ms, session {trace.session_id}"
    )
    for span in sorted(trace.spans, key=lambda s: s.start_time):
        rich_print(f"  {span.service:12} {span.operation:28} {span.duration_ms:5} ms {span.status}")
    for generation in trace.generations:
        rich_print(
            f"  generation {generation.provider}/{generation.model}: "
            f"{generation.prompt_tokens}+{generation.completion_tokens} tokens, ${generation.cost_usd:.6f}"
        )

    # traces by quality: tastiness at most 0.5
    weak = obs.query_traces(workflow_id=WORKFLOW, score_name="tastiness", max_score=0.5)
    rich_print(f"Traces of the workflow with tastiness at most 0.5: {[t.trace_id for t in weak.traces]}")

    logs = obs.query_logs(trace_id=trace_id)
    rich_print(f"Log events of the trace: {[(e.service, e.event_type) for e in logs.events]}")

    series = obs.query_metrics("recipes.ranking_ms", start_time=now_ms() - 3_600_000, aggregation="p95")
    rich_print(f"p95 ranking time over the last hour: {series[0].samples[0].value if series else 'no data'} ms")


def cost_budget_health(platform: Gogi) -> None:
    rich_print(Rule("Cost, budgets and health"))
    obs = platform.observability

    report = obs.get_cost_report(start_time=now_ms() - 86_400_000, group_by=["team", "model"])
    rich_print(f"Last 24 hours: ${report.total_cost_usd:.6f} over {report.generations} model calls")
    for bucket in report.buckets:
        rich_print(f"  {bucket.group}: ${bucket.cost_usd:.6f}")

    obs.set_budget_alert(
        BudgetAlert(name="example-10-daily", period="daily", limit_usd=1.0, filters={"workflow_id": WORKFLOW})
    )
    budget = obs.get_budget_status("example-10-daily")
    rich_print(
        f"Budget: ${budget.spent_usd:.6f} of ${budget.alert.limit_usd:.2f} today, "
        f"${budget.projected_usd:.6f} projected, {budget.state}"
    )
    obs.delete_budget_alert("example-10-daily")

    for health in obs.get_service_health():
        rich_print(f"  {health.service:12} {health.status:10} {health.reason}")


if __name__ == "__main__":
    # connect to the Gogi platform.
    # This will be the first step in any interaction with the platform, and will
    # give you access to all the available clients (indexes, documents, and queries).
    platform = Gogi(gateway_url="localhost:50051", logger=logger)
    # the name the application's telemetry is reported under
    platform.observability.service = "recipe-app"

    trace_id = suggest_recipe(platform)
    score_and_query(platform, trace_id)
    cost_budget_health(platform)
